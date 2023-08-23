from sqlmodel import Session
from .models import User, UserUpdate
from ..utils.crypt_util import get_password_hash
from fastapi import UploadFile
import uuid
import os

def save_uploaded_image(image: UploadFile) -> str:
    # Specify the directory where images will be saved
    upload_dir = "uploaded_images"

    # Create the directory if it doesn't exist
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # Generate a unique filename for the image
    filename = f"{uuid.uuid4()}.{image.filename.split('.')[-1]}"

    # Construct the full path to save the image
    image_path = os.path.join(upload_dir, filename)

    # Save the image
    with open(image_path, "wb") as f:
        f.write(image.file.read())

    return image_path


def update_user_profile(updated_user: UserUpdate, db: Session):
    user = db.query(User).filter_by(id=updated_user.id).first()
    if user:
        for attr, value in updated_user.dict(exclude_unset=True).items():
            setattr(user, attr, value)
        db.commit()
        db.refresh(user)
    return user

def update_user_password(user_id: int, new_password: str, db: Session):
    user = db.query(User).filter_by(id=user_id).first()
    if user:
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        db.refresh(user)
    return user

def update_profile_image(user_id: int, profile_image: UploadFile, db: Session):
    user = db.query(User).filter_by(id=user_id).first()
    if user:
        user.profile_photo_path = save_uploaded_image(profile_image)
        db.commit()
        db.refresh(user)
    return user

def update_cover_image(user_id: int, cover_image: UploadFile, db: Session):
    user = db.query(User).filter_by(id=user_id).first()
    if user:
        user.cover_photo_path = save_uploaded_image(cover_image)
        db.commit()
        db.refresh(user)
    return user

def update_user_bio(user_id: int, new_bio: str, db: Session):
    user = db.query(User).filter_by(id=user_id).first()
    if user:
        user.bio = new_bio
        db.commit()
        db.refresh(user)
    return user

def get_all_users(db: Session):
    return db.query(User).all()

def get_user_by_id(user_id: int, db: Session):
    return db.query(User).filter_by(id=user_id).first()
