from typing import List, Optional

from pydantic import BaseModel, Field


class ProgramRequest(BaseModel):
    performer: Optional[str] = None
    vol: Optional[str] = None


class ScheduleResponse(BaseModel):
    performer: str
    vol: str
    scheduleList: List[dict] = Field(..., alias="schedule_list")

    class Config:
        orm_mode = True
