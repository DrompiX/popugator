from pydantic import BaseModel, PositiveInt


class Task(BaseModel):
    public_id: str
    description: str
    fee: PositiveInt
    profit: PositiveInt
