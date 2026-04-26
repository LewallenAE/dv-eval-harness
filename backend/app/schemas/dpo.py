from pydantic import BaseModel
from app.schemas.hardware import Trajectory

class DPOPair(BaseModel):
    case_id: str
    prompt: str
    winner: Trajectory
    loser: Trajectory
    marginL float


class DPOBatch(BaseModel):
    pairs: list[DPOPair]
    beta: float = 0.1

