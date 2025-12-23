from uuid import UUID
from enum import Enum
from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    id: UUID
    username: str
    password: str
    email: str
    home_folder_id: UUID
    inbox_folder_id: UUID
    is_superuser: bool = False
    scopes: list[str] = []

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(from_attributes=True)


class TokenData(BaseModel):
    sub: str  # same as `user_id`
    preferred_username: str  # standard claim for `username`
    email: str
    scopes: list[str] = []

    model_config = ConfigDict(from_attributes=True)


class UserCredentials(BaseModel):
    username: str
    password: str

    model_config = ConfigDict(from_attributes=True)


class Group(BaseModel):
    id: UUID
    name: str

    # Config
    model_config = ConfigDict(from_attributes=True)


class Role(BaseModel):
    id: UUID
    name: str

    # Config
    model_config = ConfigDict(from_attributes=True)


class Permission(BaseModel):
    id: UUID
    name: str  # e.g. "Can create tags"
    codename: str  # e.g. "tag.create"

    # Config
    model_config = ConfigDict(from_attributes=True)
