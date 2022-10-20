from pydantic import BaseModel, PositiveInt


class Task(BaseModel):
    public_id: str
    jira_id: str
    description: str
    fee: PositiveInt
    profit: PositiveInt

    def get_full_name(self) -> str:
        return f'[{self.jira_id} - {self.description}]'
