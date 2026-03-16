from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from WorldState import *

class Goal:
    def __init__(self, name: str, priority: float = 1.0) -> None:
        self.Name = name
        self.Priority = priority
        # Desired boolean/int facts that must match
        self.Desired: Dict[str, int] = {}

    def is_satisfied(self, w: WorldState) -> bool:
        return all(w.B.get(k) == v for k, v in self.Desired.items())

    def heuristic(self, w: WorldState) -> int:
        # Count how many desired facts are still unsatisfied
        return sum(1 for k, v in self.Desired.items() if w.B.get(k) != v)

@dataclass
class Action:
    Name: str
    Cost: float = 1.0
    Preconditions: Dict[str, int] = field(default_factory=dict)
    Effects: Dict[str, int] = field(default_factory=dict)

    # Optional complex checks/effects at planning time
    ExtraPreconditions: Optional[Callable[[WorldState], bool]] = None
    ExtraEffects: Optional[Callable[[WorldState], None]] = None

    # Runtime hook for engine side-effects (printing here)
    Execute: Optional[Callable[[WorldState], None]] = None

    def is_applicable(self, w: WorldState) -> bool:
        for k, v in self.Preconditions.items():
            if w.B.get(k) != v:
                return False
        if self.ExtraPreconditions is not None and not self.ExtraPreconditions(w):
            return False
        return True

    def apply(self, input_state: WorldState) -> WorldState:
        w = input_state.clone()
        for k, v in self.Effects.items():
            w.B[k] = v
        if self.ExtraEffects is not None:
            self.ExtraEffects(w)
        return w

    def __str__(self) -> str:
        return self.Name



class Planner:
    @dataclass
    class _Node:
        State: WorldState
        Parent: Optional["Planner._Node"]
        Action: Optional[Action]
        G: float  # cost so far
        H: float  # heuristic
        @property
        def F(self) -> float:
            return self.G + self.H

    def plan(self,start: WorldState,goal: Goal,domain: List[Action],max_iterations: int = 2000,
    ) -> Optional[List[Action]]:
        # A* over implicit state space defined by actions
        open_list: List[Planner._Node] = []
        closed: set[str] = set()

        start_node = self._Node(State=start.clone(), Parent=None, Action=None,
                                G=0.0, H=goal.heuristic(start))
        open_list.append(start_node)

        iters = 0
        while open_list and iters < max_iterations:
            iters += 1
            # Pick node with lowest F
            best_idx = min(range(len(open_list)), key=lambda i: open_list[i].F)
            current = open_list.pop(best_idx)

            if goal.is_satisfied(current.State):
                return self._reconstruct(current)

            key = current.State.serialize()
            if key in closed:
                continue
            closed.add(key)

            # Expand applicable actions
            for action in domain:
                if not action.is_applicable(current.State):
                    continue
                next_state = action.apply(current.State)
                node = self._Node(
                    State=next_state,
                    Parent=current,
                    Action=action,
                    G=current.G + max(0.01, action.Cost),
                    H=goal.heuristic(next_state),
                )

                next_key = next_state.serialize()
                if next_key in closed:
                    continue

                # If an equal state is already in open with lower F, skip
                existing_idx = next(
                    (i for i, n in enumerate(open_list) if n.State.serialize() == next_key),
                    None,
                )
                if existing_idx is not None and open_list[existing_idx].F <= node.F:
                    continue

                open_list.append(node)

        return None  # no plan found

    def _reconstruct(self, node: "_Node") -> List[Action]:
        out: List[Action] = []
        n = node
        while n is not None and n.Action is not None:
            out.append(n.Action)
            n = n.Parent
        out.reverse()
        return out
