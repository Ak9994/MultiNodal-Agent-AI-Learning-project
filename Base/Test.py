# core_agent.py
from dataclasses import dataclass, field
from typing import List, Dict, Any
import time

# ---------- Memory ----------
@dataclass
class MemoryVar:
    text: str
    tags: List[str]
    Score: float    # 0..1 set when writing memory
    t: float = field(default_factory=lambda: time.time())

def cosine_overlap(a: str, b: str) -> float:
    # toy "relevance_score": word overlap ratio
    wa, wb = set(a.lower().split()), set(b.lower().split())
    return len(wa & wb) / max(1, len(wa | wb))

class Memory:
    def __init__(self): self.items: List[MemoryVar] = []

    def write(self, text, tags=None, Score=0.3):
        self.items.append(MemoryVar(text=text, tags=tags or [], Score=Score))

    def retrieve(self, query, k=3):
        now = time.time()
        scored = []
        for m in self.items:
            recent_score = 1.0 / (1.0 + (now - m.t) / 30.0)             
            relevance_score = cosine_overlap(query, m.text)
            Score = m.Score
            score = 0.45*recent_score + 0.4*relevance_score + 0.15*Score 
            scored.append((score, m))
        return [m for _, m in sorted(scored, key=lambda x: -x[0])[:k]]

@dataclass
class Room:
    name: str
    desc: str
    exits: Dict[str, str]  # direction -> room_name
    objects: List[str]

class World:
    def __init__(self):
        self.rooms = {
            "Hall":  Room("Hall",  "A plain hall. Door to the East is locked.", {"east":"Doorway","south":"Closet"}, []),
            "Closet":Room("Closet","A dusty closet. Something glints here.", {"north":"Hall"}, ["key"]),
            "Doorway":Room("Doorway","A heavy door bars the way East.", {"west":"Hall","east":"Outside"}, []),
            "Outside":Room("Outside","Freedom!", {}, [])
        }
        self.locked = True
        self.agent_room = "Hall"
        self.inventory = []

    def observe(self) -> str:
        r = self.rooms[self.agent_room]
        obs = f"You are in {r.name}. {r.desc}."
        if r.objects: obs += f"You see: {', '.join(r.objects)}. "
        if self.locked and self.agent_room == "Doorway": obs += "The door is locked."
        return obs.strip()

    def move(self, direction) -> str:
        r = self.rooms[self.agent_room]
        if direction in r.exits:
            dest = r.exits[direction]
            if dest == "Outside" and self.locked:
                return "The door is locked."
            self.agent_room = dest
            return f"You move {direction} to {dest}."
        return "You can't go that way."

    def take(self, obj) -> str:
        r = self.rooms[self.agent_room]
        if obj in r.objects:
            r.objects.remove(obj)
            self.inventory.append(obj)
            return f"You pick up the {obj}."
        return "There's nothing like that here."

    def use(self, obj, target) -> str:
        if obj in self.inventory and obj == "key" and target == "door" and self.agent_room == "Doorway":
            if self.locked:
                self.locked = False
                return "You unlock the door with the key. It clicks open."
        return "That doesn't seem to work."

class Planner:
    def __init__(self, memory: Memory): self.mem = memory

    def heuristic_plan(self, obs: str, inv: List[str]) -> Dict[str, Any]:
        goal = "Exit to Outside."
        notes = self.mem.retrieve("key door Outside", k=2)
        rationale = []

        if "key" not in inv:
            # If we see a key now, take it; otherwise search rooms.
            if "key" in obs.lower(): 
                return {"action":"take", "args":["key"], "why":"Need key to unlock door."}
            # Prefer exploring Closet if we recall 'glints' or saw key there
            rationale.append("Search likely places for key (Closet).")
            return {"action":"move", "args":["south"], "why":"Explore Closet for key."}

        # We have the key: navigate to door and unlock/use
        if "doorway" not in obs.lower():
            rationale.append("Head to Doorway to unlock.")
            # simple nav: from Closet go north; from Hall go east
            if "closet" in obs.lower(): return {"action":"move", "args":["north"], "why":"Back to Hall."}
            else: return {"action":"move", "args":["east"], "why":"Move to Doorway."}

        # At Doorway with key: unlock or go outside
        if "locked" in obs.lower():
            return {"action":"use", "args":["key", "door"], "why":"Unlock the door."}
        else:
            return {"action":"move", "args":["east"], "why":"Step outside to finish."}

class Agent:
    def __init__(self, world: World):
        self.world = world
        self.memory = Memory()
        self.planner = Planner(self.memory)
        self.inventory = []

    def step(self):
        obs = self.world.observe()
        self.memory.write(f"Obs: {obs}", tags=["obs"], Score=0.3)
        plan = self.planner.heuristic_plan(obs, self.inventory)
        action, args = plan["action"], plan["args"]
        outcome = self.execute(action, args)
        failure = outcome.startswith("You can't") or "doesn't seem" in outcome
        Score = 0.6 if failure else 0.4
        self.memory.write(f"Did {action} {args} -> {outcome}", tags=["act"], Score=Score)
        if failure:
            self.memory.write("Note: Try a different direction or collect the key first.", tags=["hint"], Score=0.7)
        return obs, plan, outcome

    def execute(self, action, args):
        if action == "move":  return self.world.move(args[0])
        if action == "take":  
            res = self.world.take(args[0])
            if res.startswith("You pick up"): self.inventory.append(args[0])
            return res
        if action == "use":   return self.world.use(args[0], args[1])
        return "Unknown action."


if __name__ == "__main__":
    world, agent = World(), Agent(World())
    for i in range(10):
        obs, plan, out = agent.step()
        print(f"\n Steps:{i}")
        print("Obervation:", obs)
        print("Plans:", plan["why"])
        print("Action:", plan["action"], plan["args"])
        print("Outcome:", out)
        if world.agent_room == "Outside": 
            print("Goal reached!"); break