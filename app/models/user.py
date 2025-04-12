from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List


class UserBase(SQLModel):
    username: str
    email: str
    full_name: str | None = None
    is_active: bool = True


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    
    # Activamos la relación con Profile
    profile: Optional["Profile"] = Relationship(back_populates="user")

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


# Nuevo modelo para el perfil
class ProfileBase(SQLModel):
    bio: str | None = None
    image_url: str | None = None
    location: str | None = None
    website: str | None = None


class Profile(ProfileBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="profile")


class ProfileCreate(ProfileBase):
    pass


class ProfileRead(ProfileBase):
    id: int
    user_id: int


class ProfileUpdate(SQLModel):
    bio: str | None = None
    image_url: str | None = None
    location: str | None = None
    website: str | None = None