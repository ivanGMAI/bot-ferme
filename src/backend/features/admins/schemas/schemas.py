import uuid
from pydantic import BaseModel, ConfigDict, Field


class AdminBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)


class AdminCreate(AdminBase):
    password: str = Field(..., min_length=8)


class AdminLogin(AdminBase):
    password: str


class AdminRead(AdminBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
