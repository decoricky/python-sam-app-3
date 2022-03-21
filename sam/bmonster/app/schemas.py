from typing import List

from pydantic import BaseModel


class ScheduleResponse(BaseModel):
    performer: str
    vol: str
    schedule_list: List[dict]

    class Config:
        orm_mode = True
