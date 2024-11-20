from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from blog_app.users import models, schemas, dependencies
from database import get_db
from fastapi.security import OAuth2PasswordBearer
from fastapi import Security, HTTPException



router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


@router.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = dependencies.hash_password(user.password)
    new_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Login route with JWT generation
@router.post("/login", response_model=schemas.TokenResponse)
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not dependencies.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = dependencies.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
