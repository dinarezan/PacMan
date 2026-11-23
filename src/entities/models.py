from pydantic import BaseModel, model_validator, Field
from enum import Enum
from typing import Self

GHOST_TYPES = ("blinky", "pinky", "punky", "clyde", "funky")


class BaseGhost(BaseModel):
    name: str
    position: tuple[int, int]

    @model_validator(mode='after')
    def name_validator(self) -> Self:
        if self.name.lower() not in GHOST_TYPES:
            raise ValueError("Non-existent ghost type")
        self.name = self.name.lower()
        return self


class Level(BaseModel):
    width: int = Field(ge=5, le=100)
    height: int = Field(ge=5, le=100)
    pacgum: int = Field(ge=1)
    max_time: int = Field(ge=5)
    seed: int = Field(default=0)
    ghosts: list[BaseGhost]

    @model_validator(mode='after')
    def position_validator(self) -> Self:
        failed_validation = []
        for ghost in self.ghosts:
            x, y = ghost.position
            if x >= self.width or y >= self.height or x < 0 or y < 0:
                failed_validation.append(ghost)
        if failed_validation:
            msg = ""
            for g in failed_validation:
                msg += f"{g.name} with position {g.position}\n"
            raise ValueError("Ghost position is not on the map."
                             f"Ghosts:\n{msg}")
        return self

    @model_validator(mode='after')
    def pacgum_validator(self) -> Self:
        max_pacgum = self.height * self.width - 5
        if self.pacgum > max_pacgum:
            self.pacgum = max_pacgum
        return self


class Game(BaseModel):
    levels: list[Level] = Field(min_length=1)
    lives: int = Field(ge=1)
    points_per_pacgum: int = Field(ge=0)
    points_per_super_pacgum: int = Field(ge=0)
    points_per_ghost: int = Field(ge=0)
    limit_time_per_level: int = Field(ge=1)


class Player(BaseModel):
    name: str = Field(min_length=2)
    score: int = Field(default=0, ge=0)


class Highscores(BaseModel):
    players: list[Player]


