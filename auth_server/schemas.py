from pydantic import BaseModel


class User(BaseModel):
    id: int
    is_active: bool
    password: str

    class Config:
        orm_mode = True
