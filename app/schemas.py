from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class AdminPublic(BaseModel):
    username: str


class EventBase(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=2, max_length=2000)
    event_date: datetime
    image: Optional[str] = None
    location: Optional[str] = Field(default=None, max_length=180)


class EventCreate(EventBase):
    pass


class EventUpdate(EventBase):
    pass


class EventOut(EventBase):
    id: str
    created_at: datetime
    is_past: bool


class ScheduleBase(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    teacher: str = Field(min_length=2, max_length=120)
    weekday: str = Field(min_length=2, max_length=40)
    start_time: str = Field(min_length=4, max_length=10)
    end_time: str = Field(min_length=4, max_length=10)
    hall: Optional[str] = Field(default=None, max_length=120)
    level: Optional[str] = Field(default=None, max_length=120)


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleUpdate(ScheduleBase):
    pass


class ScheduleOut(ScheduleBase):
    id: str
    created_at: datetime


class TrialRequestBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=5, max_length=40)
    direction: Optional[str] = Field(default=None, max_length=120)
    comment: Optional[str] = Field(default=None, max_length=1000)
    source: Optional[str] = Field(default=None, max_length=80)


class TrialRequestCreate(TrialRequestBase):
    pass


class TrialRequestOut(TrialRequestBase):
    id: str
    created_at: datetime
