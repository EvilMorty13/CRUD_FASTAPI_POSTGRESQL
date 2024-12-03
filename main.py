from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from blog_app.users.routes import router as user_router
from blog_app.posts.routes import router as post_router
from blog_app.comments.routes import router as comment_router
from database import Base, engine, init_db  # Ensure init_db is imported for async db initialization

# Function to handle lifespan events
async def lifespan(app: FastAPI):
    # Run the database initialization on startup
    await init_db()
    yield  # This ensures that FastAPI will continue running after the startup code is executed
    # Optional: Add shutdown logic here if needed (e.g., closing DB connections)

# Create the FastAPI application with lifespan event
app = FastAPI(lifespan=lifespan)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

# Include routers for users and posts
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(post_router, prefix="/posts", tags=["Posts"])
app.include_router(comment_router, prefix="/comments", tags=["Comments"])
