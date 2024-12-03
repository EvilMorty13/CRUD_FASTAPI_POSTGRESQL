from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from typing import List
from blog_app.posts.models import Post
from blog_app.comments.models import Comment
from blog_app.comments.schemas import CommentCreate, CommentUpdate, CommentResponse
from blog_app.users.dependencies import verify_access_token, oauth2_scheme
from blog_app.users.models import User
from database import get_db

router = APIRouter()


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )

    username = payload.get("sub")
    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Ensure the post exists
    result = await db.execute(select(Post).filter(Post.id == comment.post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    new_comment = Comment(
        user_id=current_user.id,
        post_id=comment.post_id,
        content=comment.content,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None)
    )
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment


@router.put("/{comment_id}/", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Ensure the comment exists
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    comment = result.scalars().first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    # Ensure the user is the owner of the comment
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this comment"
        )

    comment.content = comment_data.content
    comment.created_at = datetime.now(timezone.utc).replace(tzinfo=None)  # Optional: Update timestamp
    await db.commit()
    await db.refresh(comment)
    return comment


@router.delete("/{comment_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Ensure the comment exists
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    comment = result.scalars().first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    # Ensure the user is the owner of the comment
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this comment"
        )

    await db.delete(comment)
    await db.commit()
    return

@router.get("/all_comments/", response_model=List[CommentResponse])
async def get_all_comments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Comment))
    comments = result.scalars().all()
    if not comments:
        raise HTTPException(status_code=404, detail="No comments found")
    return comments
