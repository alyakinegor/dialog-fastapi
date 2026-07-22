from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from pwdlib import PasswordHash
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from sqlalchemy.exc import IntegrityError
from app.database import get_db, User

router = APIRouter(prefix='/api/auth', tags=['auth'])
password_hash = PasswordHash.recommended()
DbSession = Annotated[Session, Depends(get_db)]


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    created_at: datetime

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr 
    password: str = Field(min_length=8, max_length=128)

    @field_validator('name')
    @classmethod
    def normalize_name(cls, value: str):
        value = ' '.join(value.split())
        if len(value) < 2:
            raise ValueError('Имя должно содержать не менее 2 символов')
        return value
    

@router.post('/register', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: DbSession):
    user = User(name=payload.name, email=str(payload.email).lower(), password_hash=password_hash.hash(payload.password))

    db.add(user)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail='пользователь с таким email уже существует'

        ) from exc
    return user




