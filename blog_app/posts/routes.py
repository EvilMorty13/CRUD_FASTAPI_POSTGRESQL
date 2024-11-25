from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone
from typing import List
from database import get_db
from blog_app.users.dependencies import verify_access_token, oauth2_scheme
from blog_app.posts import models, schemas
from blog_app.users.models import User
from blog_app.tasks import send_email 

router = APIRouter()

# Helper function to get the current user
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    username = payload.get("sub")
    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

# 1. Post a blog (async)
@router.post("/", response_model=schemas.PostResponse)
async def create_post(
    post: schemas.PostCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    created_at = datetime.now(timezone.utc).replace(tzinfo=None)

    new_post = models.Post(
        user_id=current_user.id,
        title=post.title,
        content=post.content,
        created_at=created_at
    )

    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    send_email(
        subject="New Post Created",
        recipient=current_user.username,  # Assuming username is unique for demo
        body=f"Dear {current_user.username},\n\nYou created a post titled '{new_post.title}'."
    )

    return new_post

# 2. Update a blog
@router.put("/{post_id}", response_model=schemas.PostResponse)
async def update_post(post_id: int, post: schemas.PostUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(models.Post).filter(models.Post.id == post_id, models.Post.user_id == current_user.id))
    db_post = result.scalars().first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found or not authorized")
    
    if post.title:
        db_post.title = post.title
    if post.content:
        db_post.content = post.content

    await db.commit()  # Use async commit
    await db.refresh(db_post)  # Use async refresh
    return db_post

# 3. Delete a blog
@router.delete("/{post_id}")
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(models.Post).filter(models.Post.id == post_id, models.Post.user_id == current_user.id))
    db_post = result.scalars().first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found or not authorized")
    
    await db.delete(db_post)  # Use async delete
    await db.commit()  # Use async commit
    return {"message": "Post deleted successfully"}

# 4. See all blogs
@router.get("/", response_model=List[schemas.PostResponse])
async def get_all_posts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Post))
    posts = result.scalars().all()  # Fetch all posts asynchronously
    return posts

# 5. See all blogs of the current user
@router.get("/my-posts", response_model=List[schemas.PostResponse])
async def get_my_posts(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(models.Post).filter(models.Post.user_id == current_user.id))
    posts = result.scalars().all()  # Fetch user's posts asynchronously
    return posts
