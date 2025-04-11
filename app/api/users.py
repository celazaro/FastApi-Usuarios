from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.models.user import User, UserCreate, UserRead
from app.db.database import get_session
from app.core.security import get_password_hash  # importa la función

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