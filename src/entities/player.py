from pydantic import BaseModel, Field


class Player(BaseModel):
    name: str = Field(min_length=2)
    score: int = Field(default=0, ge=0)


class Highscores(BaseModel):
    players: list[Player]