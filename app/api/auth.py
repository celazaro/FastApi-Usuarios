from fastapi import APIRouter, Depends, HTTPException, status

from sqlmodel import Session, select
from app.db.database import get_session
from app.models.user import User
from app.core.security import verify_password
from app.auth.auth import create_access_token
from app.schemas.token import  LoginData

router = APIRouter()

@router.post("/login")
def login(data: LoginData, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == data.email)).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token,  "token_type": "bearer", "full_name": user.full_name, "username": user.username, }

