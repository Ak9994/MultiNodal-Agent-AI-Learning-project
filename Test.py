class GameLoop:

    def __init__(self, 
                 act: List[Action], 
                 goal: Goal, world: WorldState,
                 personality: Personality = None, 
                 delay: float = 0.0, 
                 maxlogss: int = 20):

        self.personality = personality
        self.act = act
        self.GT = goal
        self.world = world
        self.delay = delay
        self.maxlogss = maxlogss

        self.tick = 0
        self.auto = False
        self.log: List[str] = []

        self.planner = Planner()
        self.actions: List[Action] = []
        self.goal = None
        self.plan: List[Action] = []

        self.apply_personality()
        self.replan("initial")

    # -----------------------------------------------------------
    # Personality Application
    # -----------------------------------------------------------
    def apply_personality(self):
        if self.personality is None:
            self.actions = list(self.act)
            self.goal = self.desired_goal(self.GT)
            return

        self.actions = self.personality.personalized_actions(self.act)
        self.actions.extend(self.personality.interactions())
        self.goal = self.personality.personalized_goal(self.desired_goal(self.GT))
        self.personality.random_interactions(self.world)

    def desired_goal(self, g: Goal):
        new = Goal(g.Name, g.Priority)
        new.Desired = dict(g.Desired)
        return new

    def replan(self, reason: str):
        self.plan = self.planner.plan(self.world, self.goal, self.actions)
        if self.plan:
            self.logs(f"Replanned ({reason}) :: {[a.Name for a in self.plan]}")
        else:
            self.logs(f"Replanned ({reason}) :: No plan found!")

    def logs(self, msg: str):
        stamp = f"[t{self.tick:03d}]"
        line = f"{stamp} {msg}"
        self.log.append(line)
        if len(self.log) > self.maxlogss:
            self.log.pop(0)

    def snapshots(self, action: str) -> str:
        return (
            f"Executed: {action} | at={self.world.get_symfacts('at')}, "
            f"Wheat={self.world.B.get('hasWheat',0)}, "
            f"Flour={self.world.B.get('hasFlour',0)}, "
            f"Water={self.world.B.get('hasWater',0)}, "
            f"Bread={self.world.B.get('hasBread',0)}, "
            f"Hungry={self.world.B.get('hungry',0)}, "
            f"OvenLit={self.world.B.get('ovenLit',0)}, "
            f"Social={self.world.B.get('Social',0)}"
        )

    def render(self):
        print(f"RUN: {self.tick}    AUTO: {'ON' if self.auto else 'OFF'}")
        print("-"*60)

        # Map
        at = self.world.get_symfacts("at")
        def mark(x): return f"[{x}]" if x == at else f" {x} "
        print("MAP:", " -- ".join([mark("Field"), mark("Mill"), mark("Bakery")]))

        # State
        b = self.world.B
        print("STATE:",
              f"Hungry={b.get('hungry',0)}, Wheat={b.get('hasWheat',0)}, "
              f"Flour={b.get('hasFlour',0)}, Water={b.get('hasWater',0)}, "
              f"Bread={b.get('hasBread',0)}, OvenLit={b.get('ovenLit',0)}, Social={b.get('Social',0)}")

        # Goal
        print(f"GOAL: {self.goal.Name} (priority={self.goal.Priority:.2f}) :: {self.goal.Desired}")

        # Plan Preview
        if self.plan:
            names = [a.Name for a in self.plan[:8]]
            print("PLAN:", names, "..." if len(self.plan) > 8 else "")
        else:
            print("PLAN: (none)")

        # Logs
        print("LOG:")
        for l in self.log:
            print(" ", l)

        print("-"*60)
        print("Select Options: \n")
        print("[n:Next] \t")
        print("[r:Replanning] \t")
        print("[a:Auto] \t")
        print("[g:Goal] \t")
        print("[a:Auto Run] \t")
        print("[w:World] \t")
        print("[q:Quit] \t")
        print("[s:Social] \t")
        print("[p:Personality] \t")
        print("="*60)

    def steps(self):
        self.tick += 1

        # apply personality world effects
        if self.personality:
            self.personality.random_interactions(self.world)

        if not self.plan:
            self.replan("empty")
            return

        next_action = self.plan[0]

        if not next_action.is_applicable(self.world):
            self.logs(f"Action {next_action.Name} invalid → REPLAN")
            self.replan("invalid")
            return

        if next_action.Execute:
            next_action.Execute(self.world)

        self.world = next_action.apply(self.world)
        self.logs(self.snapshots(next_action.Name))
        self.plan.pop(0)

        if self.goal.is_satisfied(self.world):
            self.logs("🎯 GOAL SATISFIED!")
            self.auto = False

    # -----------------------------------------------------------
    # Main Loop
    # -----------------------------------------------------------
    def run(self):
        while True:
            self.render()

            if self.auto:
                self.steps()
                if self.delay > 0:
                    time.sleep(self.delay)
                continue

            cmd = input("> ").strip().lower()

            if cmd == "" or cmd == "n":
                self.steps()
            elif cmd == "a":
                self.auto = not self.auto
            elif cmd == "r":
                self.replan("manual")
            elif cmd == "s":
                cur = self.world.B.get("Social", 0)
                self.world.set("Social", 1-cur)
                self.logs(f"Manual Social → {1-cur}")
            elif cmd == "w":
                print(self.world.display())
                input("Enter…")
            elif cmd == "p":
                print("\nPERSONALITY:", self.personality.action_pref,
                      self.personality.goal_pref, self.personality.interaction_flags)
                input("Enter…")
            elif cmd == "q":
                print("Goodbye!")
                break
            else:
                self.logs(f"Unknown command: {cmd}")
