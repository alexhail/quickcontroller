from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    message: str


# Controller schemas
class ControllerCreate(BaseModel):
    name: str
    url: str
    access_token: str
    discovered_via: Optional[str] = None


class ControllerUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    access_token: Optional[str] = None


class ControllerResponse(BaseModel):
    id: str
    user_id: str
    name: str
    url: str
    connection_status: str
    last_seen: Optional[datetime] = None
    last_error: Optional[str] = None
    ha_version: Optional[str] = None
    discovered_via: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class DiscoveredController(BaseModel):
    name: str
    url: str
    addresses: list[str]


class TestConnectionRequest(BaseModel):
    url: str
    access_token: str


class TestConnectionResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    version: Optional[str] = None


# App schemas
class AppMetadata(BaseModel):
    app_id: str
    display_name: str
    icon: str
    default_access: bool


class AppPermission(BaseModel):
    app_id: str
    has_access: bool


# Entity/Device schemas
class EntityState(BaseModel):
    entity_id: str
    state: str
    last_changed: datetime
    last_updated: datetime
    friendly_name: Optional[str] = None
    domain: str
    attributes: dict
