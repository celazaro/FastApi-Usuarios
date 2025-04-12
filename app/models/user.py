from sqlmodel import SQLModel, Field, Relationship # type: ignore
from typing import Optional, List
from pydantic import BaseModel, HttpUrl
from fastapi import UploadFile  # Agregamos esta importación


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


class UserInfo(SQLModel):
    """Modelo para mostrar información básica del usuario"""
    username: str
    email: str
    full_name: str | None = None


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
    image: Optional[UploadFile] = None

    class Config:
        arbitrary_types_allowed = True


class ProfileRead(ProfileBase):
    id: int
    user_id: int
    user: UserInfo | None = None  # Agregamos la información del usuario
    
    def dict(self, *args, **kwargs):
        profile_dict = super().dict(*args, **kwargs)
        if profile_dict.get("image_url"):
            profile_dict["image_url"] = f"/media/{profile_dict['image_url'].split('/')[-1]}"
        return profile_dict


class ProfileFormData(ProfileBase):
    """Modelo para mostrar los datos actuales del formulario"""
    user_info: UserInfo
    
    def dict(self, *args, **kwargs):
        form_dict = super().dict(*args, **kwargs)
        if form_dict.get("image_url"):
            form_dict["image_url"] = f"/media/{form_dict['image_url'].split('/')[-1]}"
        return form_dict


class ProfileUpdate(SQLModel):
    bio: str | None = None
    image: Optional[UploadFile] = None
    location: str | None = None
    website: str | None = None

    class Config:
        arbitrary_types_allowed = True