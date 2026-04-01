import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from .enums import Environment, UserDomain


class UserBase(BaseModel):
    login: EmailStr
    project_id: uuid.UUID
    env: Environment
    domain: UserDomain


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserRead(UserBase):
    id: uuid.UUID
    locktime: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLockRequest(BaseModel):
    project_id: uuid.UUID
    env: Environment
    domain: UserDomain
