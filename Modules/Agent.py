from Memory import *
from World import *
class planner:
    def __init__(self,Memory:Memory):
        self.memory = Memory

    def heuristic_plan(self,observe:str,inv:list[str])->dict[str,any]:
        Goal = "escape the room"
        Notes = self.memory.retrieve("key",k=3)
        logic = []
        #Clue to finding the key
        if "key" not in inv:
            if "key" in observe.lower():
                return {"action":"pickup",
                        "args":["key"],
                        "Reason":"Need Key to unlock door"}
            logic.append("Check Closet for key")
            return {"action":"move",
                    "args":["South"],
                    "Reason":"Key in Closet , head south!"}
        #find the exit if key is found
        if "Doorway" in observe.lower():
            logic.append("Head to Doorway to exit")
            #from Doorway , head east towards exit
            if "Closet" in observe.lower():
                return { "action":"move",
                         "args":["North"],
                         "Reason":"Back to Hall"}
            else:
                return { "action":"move",
                         "args":["East"],
                         "Reason":"Head to Doorway"}
        #Doorway
        if "Locked" in observe.lower():
            return { "action":"open",
                     "args":["key","door"],
                     "Reason":"use key to unlock door"}
        else:
            return { "action":"exit",
                     "args":["east"],
                     "Reason":"Exit through door"}
        
class Agent:
    def __init__(self,World:world):
        self.world = World
        self.memory = Memory()
        self.planner = planner(self.memory)
        self.inventory = []
    #calculate outcome of action
    def execute(self,action,args):
        if action == "move": return self.world.agent_action(args[0])
        if action == "pickup": 
            outcome = self.world.agent_pickup(args[0])
            if outcome.startswith("You picked up"):
                self.inventory.append(args[0])
        if action == "use":
            return self.world.agent_use(args[0],args[1])
        return "Unknow action"
    #Show result for each interaction
    def step(self):
        observation = self.world.agent_interaction()
        plan = self.planner.heuristic_plan(observation,self.inventory)
        action = plan["action"]
        args = plan["args"]
        self.memory.write(f"Observation:{observation}",
                          tags=["observation"],
                          score=0.5)
        result = self.execute(action,args)

        #show Result based on action with helpful hints
        failure = result.startswith("You can't") or ("Doesnt seem") in result
        score = 0.6 if failure else 0.4
        self.memory.write(f"Took {action} {args} -> {result}",
                            tags=["action"],
                            score=score)
        if failure:
            self.memory.write("Hint: Try diff direction / get Key first",
                                tags=["hint"],
                                score=0.7)
        return observation, plan, result
            


        
        
        
        


    
            

            