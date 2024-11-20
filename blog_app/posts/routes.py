from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from blog_app.users.dependencies import verify_access_token, oauth2_scheme
from blog_app.posts import models, schemas
from blog_app.users.models import User

router = APIRouter()

# Helper function to get the current user
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

# 1. Post a blog
@router.post("/", response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_post = models.Post(user_id=current_user.id, title=post.title, content=post.content)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# 2. Update a blog
@router.put("/{post_id}", response_model=schemas.PostResponse)
def update_post(post_id: int, post: schemas.PostUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id, models.Post.user_id == current_user.id).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found or not authorized")
    if post.title:
        db_post.title = post.title
    if post.content:
        db_post.content = post.content
    db.commit()
    db.refresh(db_post)
    return db_post

# 3. Delete a blog
@router.delete("/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id, models.Post.user_id == current_user.id).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found or not authorized")
    db.delete(db_post)
    db.commit()
    return {"message": "Post deleted successfully"}

# 4. See all blogs
@router.get("/", response_model=List[schemas.PostResponse])
def get_all_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts

# 5. See all blogs of the current user
@router.get("/my-posts", response_model=List[schemas.PostResponse])
def get_my_posts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    posts = db.query(models.Post).filter(models.Post.user_id == current_user.id).all()
    return posts
