from uuid import UUID
from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    id: UUID
    username: str
    email: str

    model_config = ConfigDict(from_attributes=True)



class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

    model_config = ConfigDict(from_attributes=True)


class UserCredentials(BaseModel):
    username: str
    password: str

    model_config = ConfigDict(from_attributes=True)
