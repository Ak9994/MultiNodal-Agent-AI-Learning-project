from typing import Dict, Optional

class WorldState:
    def __init__(self) -> None:
        self.B: Dict[str, int] = {}
        self.S: Dict[str, str] = {}

    def clone(self) -> "WorldState":
        world = WorldState()
        world.B = dict(self.B)
        world.S = dict(self.S)
        return world

    # Boolean/int facts
    def has(self, key: str, value: int = 1) -> bool:
        return self.B.get(key) == value

    def set(self, key: str, value: int) -> None:
        self.B[key] = value

    # Symbolic facts
    def get_symfacts(self, key: str) -> Optional[str]:
        return self.S.get(key)

    def set_symfacts(self, key: str, value: str) -> None:
        self.S[key] = value

    def serialize(self) -> str:
        # Deterministic string for state equality in planner
        b = ",".join(f"{k}={self.B[k]}" for k in sorted(self.B))
        s = ",".join(f"{k}={self.S[k]}" for k in sorted(self.S))
        return f"B[{b}]|S[{s}]"

    # Pretty helper
    def display(self) -> str:
        return f"WorldState(B={self.B}, S={self.S})"