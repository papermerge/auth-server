from pydantic import BaseModel


class User(BaseModel):
    id: int
    is_active: bool
    password: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str
