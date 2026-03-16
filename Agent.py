from GOAP import *

class Agent:
    def __init__(self, domain: List[Action], goal: Goal, start: WorldState) -> None:
        self.plan = Planner()
        self.location = domain
        self.result = goal
        self.world = start

    def run(self) -> None:
        print("== Agent starts planning ==")
        plan = self.plan.plan(self.world, self.result, self.location)
        if not plan:
            print("No plan found!")
            return

        print("Plan found:")
        for a in plan:
            print(f"  - {a.Name}")

        print("\n== Executing plan ==")
        for action in plan:
            # (Optional) runtime applicability check for dynamic worlds
            if not action.is_applicable(self.world):
                print(f"Action '{action.Name}' no longer applicable. Replanning...")
                plan = self.plan.plan(self.world, self.result, self.location)
                if not plan:
                    print("Replan failed.")
                    return
                continue

            # Engine-side effect
            if action.Execute:
                action.Execute(self.world)

            # Model-side effect
            self.world = action.apply(self.world)

            print(
                f"Executed: {action.Name} | "
                f"at={self.world.get_symfacts('at')}, "
                f"Wheat={self.world.B.get('hasWheat',0)}, "
                f"Flour={self.world.B.get('hasFlour',0)}, "
                f"Water={self.world.B.get('hasWater',0)}, "
                f"Bread={self.world.B.get('hasBread',0)}, "
                f"Hungry={self.world.B.get('hungry',0)}, "
                f"OvenLit={self.world.B.get('ovenLit',0)}"
            )

        print("\n== Finished ==")
        print(f"Goal satisfied? {self.result.is_satisfied(self.world)}")

