from Domain import *
from Agent import *
from Personality import *
import sys

def main() -> int:
    actions = Domain.create_actions()
    goal = Domain.create_goal_make_and_eat_bread()
    start = Domain.create_initial_world()

    agent = Agent(actions, goal, start)
    agent.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())