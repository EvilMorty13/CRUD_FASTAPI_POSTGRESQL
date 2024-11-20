from fastapi import FastAPI
from blog_app.users.routes import router as user_router
from blog_app.posts.routes import router as post_router
from database import Base, engine
from fastapi.security import OAuth2PasswordBearer

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

# Include routers
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(post_router, prefix="/posts", tags=["Posts"])

