from WorldState import *
from GOAP import *

class Domain:
    @staticmethod
    def set_location(loc: str) -> Callable[[WorldState], None]:
        def _f(w: WorldState) -> None:
            w.set_symfacts("at", loc)
        return _f

    @staticmethod
    def create_actions() -> List[Action]:
        actions: List[Action] = []

        actions.append(Action(
            Name="MoveToField", Cost=2.0,
            ExtraEffects=Domain.set_location("Field")
        ))
        actions.append(Action(
            Name="MoveToMill", Cost=2.0,
            ExtraEffects=Domain.set_location("Mill")
        ))
        actions.append(Action(
            Name="MoveToBakery", Cost=2.0,
            ExtraEffects=Domain.set_location("Bakery")
        ))

        actions.append(Action(
            Name="GatherWheat",
            Preconditions={"hasWheat": 0},
            ExtraPreconditions=lambda w: w.get_symfacts("at") == "Field",
            Effects={"hasWheat": 1},
            Execute=lambda w: print("…gathers wheat at the field \n")
        ))

        actions.append(Action(
            Name="MillFlour",
            Preconditions={"hasWheat": 1},
            ExtraPreconditions=lambda w: w.get_symfacts("at") == "Mill",
            Effects={"hasWheat": 0, "hasFlour": 1},
            Execute=lambda w: print("…mills flour at the mill \n")
        ))

        actions.append(Action(
            Name="FetchWater",
            Preconditions={"hasWater": 0},
            ExtraPreconditions=lambda w: w.get_symfacts("at") == "Bakery",
            Effects={"hasWater": 1},
            Execute=lambda w: print("…fetches water at the bakery well \n")
        ))

        actions.append(Action(
            Name="LightOven",
            Preconditions={"ovenLit": 0},
            ExtraPreconditions=lambda w: w.get_symfacts("at") == "Bakery",
            Effects={"ovenLit": 1},
            Execute=lambda w: print("…lights the bakery oven \n")
        ))

        actions.append(Action(
            Name="BakeBread",
            Preconditions={"hasFlour": 1, "hasWater": 1, "ovenLit": 1},
            ExtraPreconditions=lambda w: w.get_symfacts("at") == "Bakery",
            Effects={"hasBread": 1, "hasFlour": 0, "hasWater": 0},
            Execute=lambda w: print("…bakes a loaf of bread \n")
        ))

        actions.append(Action(
            Name="EatBread",
            Preconditions={"hasBread": 1, "hungry": 1},
            Effects={"hasBread": 0, "hungry": 0},
            Execute=lambda w: print("…eats the bread \n")
        ))

        return actions

    @staticmethod
    def create_goal_make_and_eat_bread() -> Goal:
        g = Goal("MakeAndEatBread", priority=1.0)
        g.Desired["hungry"] = 0
        # If you want to end with spare bread, also require:
        # g.Desired["hasBread"] = 1
        return g

    @staticmethod
    def create_initial_world() -> WorldState:
        w = WorldState()
        w.set_symfacts("at", "Field")
        w.set("hungry", 1)
        w.set("hasWheat", 0)
        w.set("hasFlour", 0)
        w.set("hasWater", 0)
        w.set("hasBread", 0)
        w.set("ovenLit", 0)
        return w
