from typing import Dict, Optional, List
from dataclasses import dataclass, field
import random
from GOAP import Action, Goal, WorldState


@dataclass
class Personality:
    NPC_name: str
    rng: random.Random = field(default_factory=random.Random)
    action_pref: Dict[str, float] = field(default_factory=dict)
    goal_pref: Dict[str, float] = field(default_factory=dict)
    interaction_flags: Dict[str, float] = field(default_factory=dict)

    @classmethod
    def Randomization(cls, Name: str, seed: Optional[int] = None):
        rng = random.Random(seed)

        def pick(a=0.5, b=1.5):
            return round(rng.uniform(a, b), 2)

        return cls(
            NPC_name=Name,
            rng=rng,
            action_pref={
                "MoveToField": pick(),
                "MoveToMill": pick(),
                "MoveToBakery": pick(),
                "GatherWheat": pick(),
                "MillFlour": pick(),
                "FetchWater": pick(),
                "LightOven": pick(),
                "BakeBread": pick(),
                "EatBread": pick(),
                "ChatWithNPC": pick(),
            },
            goal_pref={
                "HaveBread": pick(),
                "HaveFlour": pick(),
                "HaveWater": pick(),
                "HaveWheat": pick(),
                "BeFull": pick(),
                "BakeBread": pick(),
            },
            interaction_flags={
                "Social": 0.2
            }
        )

    # Modify actions based on preferences
    def personalized_actions(self, actions: List[Action]) -> List[Action]:
        new_actions = []
        for a in actions:
            mod = self.action_pref.get(a.Name, 1.0)
            new_actions.append(
                Action(
                    Name=a.Name,
                    Cost=max(0.1, a.Cost * mod),
                    Preconditions=dict(a.Preconditions),
                    Effects=dict(a.Effects),
                    ExtraPreconditions=a.ExtraPreconditions,
                    ExtraEffects=a.ExtraEffects,
                    Execute=a.Execute
                )
            )
        return new_actions

    # Modify goal priorities
    def personalized_goal(self, goal: Goal) -> Goal:
        mod = self.goal_pref.get(goal.Name, 1.0)
        new_goal = Goal(goal.Name, priority=goal.Priority * mod)
        new_goal.Desired = dict(goal.Desired)
        return new_goal

    # Randomly activate social flags in the world
    def random_interactions(self, world: WorldState):
        for flag, chance in self.interaction_flags.items():
            world.set(flag, 1 if self.rng.random() < chance else 0)

    # Add special "Chat" action
    def interactions(self) -> List[Action]:
        def can_chat(world: WorldState) -> bool:
            return (
                world.get_symfacts("at") == "Bakery"
                and world.B.get("Social", 0) == 1
            )

        return [
            Action(
                Name="ChatWithNPC",
                Cost=0.5 * self.action_pref.get("ChatWithNPC", 1.0),
                ExtraPreconditions=can_chat,
                Effects={},
                Execute=lambda w: print("NPC chats and gains information!")
            )
        ]
