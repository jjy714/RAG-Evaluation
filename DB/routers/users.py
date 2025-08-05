# routers/users.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.database import Database

from .. import crud, models, auth
from ..database import db # database.py에서 설정한 db 객체 가져오기

router = APIRouter()

# --- 데이터베이스 의존성 주입 ---
def get_db():
    return db

@router.post("/users", status_code=status.HTTP_201_CREATED, summary="회원가입")
def register_user(user: models.UserCreate, db: Database = Depends(get_db)):
    db_user = crud.get_user(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다."
        )
    crud.create_user(db=db, user=user)
    return {"message": "회원가입이 성공적으로 완료되었습니다."}

@router.post("/login", response_model=models.Token, summary="로그인")
def login_for_access_token(db: Database = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.get_user(db, email=form_data.username) # form_data.username에 이메일이 담김
    if not user or not auth.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 정확하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 액세스 토큰 생성
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}