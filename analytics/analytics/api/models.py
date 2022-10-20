from datetime import date
from enum import Enum

from pydantic import BaseModel


class Period(str, Enum):
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'


class CumulativeAnalytics(BaseModel):
    management_earned: int
    negative_income_popugs: int


class TopTaskInfo(BaseModel):
    date: date
    desctiption: str
    price: int
