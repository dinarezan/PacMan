class PacMan:
    def __init__(self, pos: tuple[float, float]):
        self.position: tuple[float, float] = pos
        self.direction: tuple[int, int, int, int] = (1, 0, 0, 0)
        # (N, E, S, W)
        # (1, 0, 0, 0) means looking towards north


class PacGum:
    def __init__(self, position: tuple[int, int]):
        self.position: tuple[int, int] = position
        self.eaten: bool = False
        self.super: bool = False


class PacGumFactory:
    @staticmethod
    def create(maze: list[list[int]], number: int) -> list[PacGum]:
        pass