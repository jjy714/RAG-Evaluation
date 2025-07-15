from sqlalchemy.orm import Session
from . import models, schemas
from uuid import UUID

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    # In a real app, you'd hash the password here
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(
        email=user.email, 
        username=user.username, 
        hashed_password=fake_hashed_password,
        role='user'  # Explicitly set role to 'user'
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_role(db: Session, user_id: int, role: str):
    db_user = get_user(db, user_id)
    if db_user:
        db_user.role = role
        db.commit()
        db.refresh(db_user)
    return db_user

def get_session(db: Session, session_id: UUID):
    return db.query(models.Session).filter(models.Session.session_id == session_id).first()

def create_session(db: Session, session: schemas.SessionCreate):
    db_session = models.Session(user_id=session.user_id, rag_config=session.rag_config)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session
