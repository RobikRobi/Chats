from pydantic import BaseModel



class RegUser(BaseModel):

    username: str
    password: str | bytes


class UserShema(BaseModel):

    id: int
    username: str