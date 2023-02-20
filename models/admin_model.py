from pydantic import BaseModel


class RegisClientUserModel(BaseModel):
    username: str
    password: str
    fullname: str


class ResetPasswordModel(BaseModel):
    password: str
