from uuid import UUID
from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    id: UUID
    username: str
    password: str
    email: str
    home_folder_id: UUID
    inbox_folder_id: UUID

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

    model_config = ConfigDict(from_attributes=True)


class UserCredentials(BaseModel):
    username: str
    password: str

    model_config = ConfigDict(from_attributes=True)
