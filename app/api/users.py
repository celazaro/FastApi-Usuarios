from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Optional

from app.models.user import User, UserCreate, UserRead, UserUpdate, Profile
from app.db.database import get_session
from app.core.security import get_password_hash  # importa la función
from app.auth.auth import get_current_user
from app.utils.image_handler import delete_image

router = APIRouter()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    # Verificamos si el email o username ya existe
    statement = select(User).where((User.email == user.email) | (User.username == user.username))
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    hashed_pw = get_password_hash(user.password)
    db_user = User(
    username=user.username,
    email=user.email,
    full_name=user.full_name,
    is_active=user.is_active,
    #hashed_password=user.password  
    hashed_password=hashed_pw # más adelante aquí irá el hash real
)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get("/", response_model=list[UserRead])
def list_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.patch("/me", response_model=UserRead)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Actualizar datos del usuario actual"""
    # Verificar si el email o username ya existe (si se están actualizando)
    if user_update.email or user_update.username:
        statement = select(User).where(
            (User.id != current_user.id) &  # Excluir el usuario actual
            ((User.email == user_update.email) | (User.username == user_update.username))
        )
        existing_user = session.exec(statement).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="El email o username ya está en uso"
            )

    # Actualizar solo los campos proporcionados
    update_data = user_update.dict(exclude_unset=True)
    
    # Si se proporciona una nueva contraseña, hashearla
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for key, value in update_data.items():
        setattr(current_user, key, value)
    
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    
    return current_user

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Eliminar el usuario actual y su perfil"""
    try:
        # Primero, eliminar el perfil si existe
        profile = session.exec(
            select(Profile).where(Profile.user_id == current_user.id)
        ).first()
        
        if profile:
            try:
                # Si el perfil tiene una imagen, eliminarla
                if profile.image_url:
                    await delete_image(profile.image_url)
            except Exception as e:
                # Si hay un error al eliminar la imagen, lo registramos pero continuamos
                print(f"Error al eliminar la imagen: {str(e)}")
            
            # Eliminar el perfil
            session.delete(profile)
            session.commit()  # Commit separado para el perfil
        
        # Eliminar el usuario
        session.delete(current_user)
        session.commit()
        
        return None
        
    except Exception as e:
        session.rollback()  # Revertir cambios en caso de error
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar el usuario: {str(e)}"
        )

@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user: User = Depends(get_current_user)
):
    """Obtener datos del usuario actual"""
    return current_user