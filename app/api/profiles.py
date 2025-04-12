from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.models.user import Profile, ProfileCreate, ProfileRead, ProfileUpdate
from app.db.database import get_session
from app.auth.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=ProfileRead)
def create_profile(
    profile: ProfileCreate,
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

    db_profile = Profile(
        **profile.dict(),
        user_id=current_user.id
    )
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)
    return db_profile


@router.get("/me", response_model=ProfileRead)
def get_my_profile(
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    profile = session.exec(
        select(Profile).where(Profile.user_id == current_user.id)
    ).first()
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Perfil no encontrado"
        )
    return profile


@router.patch("/me", response_model=ProfileRead)
def update_my_profile(
    profile_update: ProfileUpdate,
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
    
    profile_data = profile_update.dict(exclude_unset=True)
    for key, value in profile_data.items():
        setattr(db_profile, key, value)
    
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)
    return db_profile 