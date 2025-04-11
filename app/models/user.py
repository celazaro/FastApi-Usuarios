from sqlmodel import SQLModel, Field



class UserBase(SQLModel):
    username: str
    email: str
    full_name: str | None = None
    is_active: bool = True


class User (UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str

    # Relaciones futuras (opcional, por ahora dejamos la estructura)
    # posts: list["Post"] = Relationship(back_populates="user")
    # profile: "Profile" = Relationship(back_populates="user")
    
   


class UserCreate(UserBase):
    password: str  # Esto es lo que nos llega en el registro


class UserRead(UserBase):
    id: int


class UserUpdate(SQLModel):
    username: str | None = None
    email: str | None = None
    full_name: str | None = None
    password: str | None = None
    is_active: bool | None = None