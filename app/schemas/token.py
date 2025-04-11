from sqlmodel import SQLModel


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class LoginData(SQLModel):
    email: str
    password: str