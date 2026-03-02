from Memory import *
from Agent import *
from World import *

if __name__ == "__main__":
    World = world()
    agent = Agent(World)
    for testrun in range(10):
        observation, plan, outcome = agent.step()
        print(f"Steps:{testrun}")
        print("OBSERVATION:", observation)
        print("THINK:", plan["Reason"])
        print("ACT:", plan["action"], plan["args"])
        print("OUTCOME:", outcome)
        if World.agent_room == "Outside":
            print("Exited successfully!")
            break
