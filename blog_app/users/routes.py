from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select  # To use AsyncSession for querying
from blog_app.users import models, schemas, dependencies
from database import get_db
from fastapi.security import OAuth2PasswordBearer
from fastapi import Security

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


@router.post("/register", response_model=schemas.UserResponse)
async def register_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # Use async query with 'select'
    result = await db.execute(select(models.User).filter(models.User.username == user.username))
    db_user = result.scalars().first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    result = await db.execute(select(models.User).filter(models.User.email == user.email))
    db_user = result.scalars().first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = dependencies.hash_password(user.password)
    new_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password,age=user.age)
    db.add(new_user)
    await db.commit()  # Use async commit
    await db.refresh(new_user)  # Use async refresh
    return new_user

# Login route with JWT generation
@router.post("/login", response_model=schemas.TokenResponse)
async def login_user(user: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).filter(models.User.username == user.username))
    db_user = result.scalars().first()
    if not db_user or not dependencies.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = dependencies.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
