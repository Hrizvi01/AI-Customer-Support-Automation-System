from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

Category = Literal['billing', 'technical', 'account', 'general']
Priority = Literal['low', 'medium', 'high']
Status = Literal['open', 'in_progress', 'resolved']


class TicketCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    subject: str = Field(min_length=3, max_length=180)
    description: str = Field(min_length=10, max_length=10000)
    customer_name: str = Field(min_length=1, max_length=100)
    customer_email: str = Field(min_length=3, max_length=254, pattern=r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
    category: Category | None = None
    priority: Priority | None = None


class TicketUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    subject: str | None = Field(default=None, min_length=3, max_length=180)
    description: str | None = Field(default=None, min_length=10, max_length=10000)
    status: Status | None = None
    category: Category | None = None
    priority: Priority | None = None

    @field_validator('subject', 'description', 'status', 'category', 'priority', mode='before')
    @classmethod
    def reject_null(cls, value: object) -> object:
        if value is None:
            raise ValueError('Omit unchanged fields instead of sending null.')
        return value


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    subject: str
    description: str
    customer_name: str
    customer_email: str
    status: str
    category: str | None
    priority: str | None
    sentiment: str | None
    analysis: dict | None
    suggested_reply: str | None
    reply_model: str | None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None


class TextRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    text: str = Field(min_length=3, max_length=10000)


class ReplyRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    instructions: str = Field(default='', max_length=1000)
