from typing import Dict,Optional
from dataclasses import field
import random
from GOAP import *
@dataclass
class Personality:
    NPC_name:str
    rng: random.Random = field(default_factory=random.Random)
    # Multipliers: >1.0 = likes , <1.0 = dislikes
    action_pref: Dict[str,float] = field(default_factory=dict)
    goal_pref: Dict[str,float] = field(default_factory=dict)
    #Flag for Interaction either +/-
    interaction_flags:Dict[str,float] = field(default_factory=dict)
    
    @classmethod
    def Randomization(cls,Name:str,seed:Optional[int]=None):
        rng = random.Random(seed)

        def pick(a=0.5,b=1.0):
            return round(random.uniform(a,b))
        
        return cls(
            NPC_name = Name,
            rng = rng,
            action_pref = {
                "MoveToField": pick(),
                "MoveToMill": pick(),
                "MoveToBakery": pick(),
                "GatherWheat": pick(),
                "MillFlour": pick(),
                "FetchWater": pick(),
                "LightOven": pick(),
                "BakeBread": pick(),
                "EatBread": pick(),
                "ChatWithNPC": pick()
            }, 
            goal_pref = {
                "HaveBread": pick(),
                "HaveFlour": pick(),
                "HaveWater": pick(),
                "HaveWheat": pick(),
                "BeFull": pick(),
                "BakeBread":pick()
            }, 
            interaction_flags = {
                "Social":0.2
            }
        )
    
    def personalized_actions(self,actions:list[Action])->list[Action]:
        act:list[Action] = []

        for sel in actions:
            action_score = self.action_pref.get(sel.Name,1.0)
            action_selection = Action(Name = sel.Name,Cost=max(0.1,sel.Cost*action_score),
                                      Preconditions=dict(sel.Preconditions),
                                      Effects=dict(sel.Effects),
                                      ExtraPreconditions= sel.ExtraPreconditions,
                                      ExtraEffects=sel.ExtraEffects, 
                                      Execute= sel.Execute)
            act.append(action_selection)
        return act
    
    def personalized_goal(self,goal:Goal)->Goal:
        #Return goals with score
        GS = Goal(goal.Name,priority=goal.Priority*self.goal_pref.get(goal.Name,1.0))
        GS.Desired= dict(GS.Desired)
        return GS
    
    def random_interactions(self,world:WorldState)->None:
        for flag,p in self.interaction_flags.items():
            if self.rng.random() < p:
                set_interaction = 1 
            else:
                set_interaction = 0
        world.set(flag,set_interaction)


    def interactions(self)->List[Action]:
        def social_interaction(world:WorldState)->bool:
            return (world.get_symfacts("at")=="Bakery") and (world.B.get("Social",0)==1)
        
        return [
            Action(
                Name="Chat with other NPC",
                Cost=0.5*self.action_pref.get("ChatWithNPC",1.0),
                ExtraPreconditions= social_interaction,
                Execute = lambda _: print("...collected info"),
                Effects={}
            )
        ]
        
        

        



    




    





    
    

    

    

    



