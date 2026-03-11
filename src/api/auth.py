from db.models import User
from fastapi import APIRouter, HTTPException, Depends
from services.security import hash_password, verify_password
from schemas.user import UserRegister, UserResponse, UserLogin, TokenResponse
from sqlalchemy.orm import Session
from db.database import get_db
from config import SECRET
import jwt
from datetime import datetime, timedelta

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {
        "sub": str(db_user.id),
        "username": db_user.username,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    token = jwt.encode(payload, SECRET, algorithm="HS256")
    return TokenResponse(access_token=token)