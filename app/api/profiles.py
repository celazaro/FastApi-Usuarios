from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlmodel import Session, select
from typing import Optional
from fastapi.encoders import jsonable_encoder

from app.models.user import (
    Profile, ProfileCreate, ProfileRead, ProfileUpdate, 
    ProfileFormData, User, UserInfo
)
from app.db.database import get_session
from app.auth.auth import get_current_user
from app.utils.image_handler import save_image, delete_image

router = APIRouter()

@router.post("/", response_model=ProfileRead)
async def create_profile(
    bio: str = Form(None),
    location: str = Form(None),
    website: str = Form(None),
    image: UploadFile = File(None),
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verificar si el usuario ya tiene un perfil
    existing_profile = session.exec(
        select(Profile).where(Profile.user_id == current_user.id)
    ).first()
    
    if existing_profile:
        raise HTTPException(
            status_code=400,
            detail="El usuario ya tiene un perfil"
        )

    # Procesar la imagen si se proporcionó una
    image_path = None
    if image:
        try:
            image_path = await save_image(image)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # Crear el perfil
    db_profile = Profile(
        bio=bio,
        location=location,
        website=website,
        image_url=image_path,
        user_id=current_user.id
    )
    
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)
    return db_profile


@router.get("/me/form", response_model=ProfileFormData)
def get_profile_form_data(
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Obtener los datos actuales del perfil para el formulario de edición"""
    profile = session.exec(
        select(Profile).where(Profile.user_id == current_user.id)
    ).first()
    
    if not profile:
        # Si no existe el perfil, devolver solo los datos del usuario
        return ProfileFormData(
            bio=None,
            image_url=None,
            location=None,
            website=None,
            user_info=UserInfo(
                username=current_user.username,
                email=current_user.email,
                full_name=current_user.full_name
            )
        )
    
    # Si existe el perfil, devolver todos los datos
    return ProfileFormData(
        bio=profile.bio,
        image_url=profile.image_url,
        location=profile.location,
        website=profile.website,
        user_info=UserInfo(
            username=current_user.username,
            email=current_user.email,
            full_name=current_user.full_name
        )
    )

@router.get("/me", response_model=ProfileRead)
def get_my_profile(
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Obtener el perfil completo con datos del usuario"""
    profile = session.exec(
        select(Profile).where(Profile.user_id == current_user.id)
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Perfil no encontrado"
        )
    
    # Agregar información del usuario al perfil
    user_info = UserInfo(
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name
    )
    
    return ProfileRead(
        id=profile.id,
        user_id=profile.user_id,
        bio=profile.bio,
        image_url=profile.image_url,
        location=profile.location,
        website=profile.website,
        user=user_info
    )


@router.patch("/me", response_model=ProfileRead)
async def update_my_profile(
    bio: str = Form(None),
    location: str = Form(None),
    website: str = Form(None),
    image: UploadFile = File(None),
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    db_profile = session.exec(
        select(Profile).where(Profile.user_id == current_user.id)
    ).first()
    
    if not db_profile:
        raise HTTPException(
            status_code=404,
            detail="Perfil no encontrado"
        )
    
    # Procesar la imagen solo si se proporciona una nueva
    if image and image.filename:
        try:
            # Eliminar la imagen anterior si existe
            if db_profile.image_url:
                await delete_image(db_profile.image_url)
            # Guardar la nueva imagen
            image_path = await save_image(image)
            db_profile.image_url = image_path
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # Actualizar solo los campos que se proporcionaron
    if bio is not None and bio.strip():  # Actualizar solo si no está vacío
        db_profile.bio = bio
    if location is not None and location.strip():
        db_profile.location = location
    if website is not None and website.strip():
        db_profile.website = website
    
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)
    
    # Incluir información del usuario en la respuesta
    return ProfileRead(
        id=db_profile.id,
        user_id=db_profile.user_id,
        bio=db_profile.bio,
        image_url=db_profile.image_url,
        location=db_profile.location,
        website=db_profile.website,
        user=UserInfo(
            username=current_user.username,
            email=current_user.email,
            full_name=current_user.full_name
        )
    )


@router.get("/{user_id}", response_model=ProfileRead)
def get_user_profile(
    user_id: int,
    session: Session = Depends(get_session)
):
    """Obtener el perfil de cualquier usuario con sus datos"""
    profile = session.exec(
        select(Profile).where(Profile.user_id == user_id)
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Perfil no encontrado"
        )
    
    # Obtener el usuario asociado al perfil
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )
    
    # Agregar información del usuario al perfil
    user_info = UserInfo(
        username=user.username,
        email=user.email,
        full_name=user.full_name
    )
    
    return ProfileRead(
        id=profile.id,
        user_id=profile.user_id,
        bio=profile.bio,
        image_url=profile.image_url,
        location=profile.location,
        website=profile.website,
        user=user_info
    ) 