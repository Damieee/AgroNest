from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlmodel import Session
from typing import List
from .models import UserUpdate, UserRead
from ..common.models import ResponseModel
from ..auth.views import authenticate_user
from core.engine import get_db
from .crud import get_all_users, get_user_by_id, update_user_profile, update_user_password, update_profile_image, update_cover_image, update_user_bio

from ..auth.models import LoginRequest


router = APIRouter()

@router.put("/update_profile",
            response_model=ResponseModel,
            status_code=status.HTTP_200_OK,
            responses={
                status.HTTP_200_OK:
                ResponseModel.example(
                    description='Profile Updated',
                    data=UserRead().dict(),
                ),
                status.HTTP_400_BAD_REQUEST: {"model": ResponseModel},
                status.HTTP_403_FORBIDDEN: {"model": ResponseModel},
                status.HTTP_404_NOT_FOUND: {"model": ResponseModel},
            }
            )
async def update_profile(
        updated_user: UserUpdate,
        db: Session = Depends(get_db),
        # Authenticate user
        user = authenticate_user(request.identifier, request.password, db)
):
    if updated_user.email != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this profile",
        )

    user = update_user_profile(updated_user, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return ResponseModel.success(
        message="Profile Updated",
        data=user,
    )

@router.put("/update_password")
async def update_password(
    user_id: int,
    new_password: str,
    db: Session = Depends(get_db)
):
    user = update_user_password(user_id, new_password, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return ResponseModel.success(message="Password Updated", data=None)

@router.post("/update_profile_image")
async def update_profile_image(
    user_id: int,
    profile_image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = update_profile_image(user_id, profile_image, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return ResponseModel.success(message="Profile Image Updated", data=user)

@router.post("/update_cover_image")
async def update_cover_image(
    user_id: int,
    cover_image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = update_cover_image(user_id, cover_image, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return ResponseModel.success(message="Cover Image Updated", data=user)

@router.put("/update_bio")
async def update_bio(
    user_id: int,
    new_bio: str,
    db: Session = Depends(get_db)
):
    user = update_user_bio(user_id, new_bio, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return ResponseModel.success(message="Bio Updated", data=user)

@router.get("/all_users")
async def get_all_users(
    db: Session = Depends(get_db)
):
    users = get_all_users(db)
    return ResponseModel.success(message="Users fetched successfully", data=users)

@router.get("/get_user")
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return ResponseModel.success(message="User fetched successfully", data=user)

