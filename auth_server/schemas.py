from pydantic import BaseModel


class User(BaseModel):
    id: str
    username: str
    email: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class UserCredentials(BaseModel):
    username: str
    password: str

