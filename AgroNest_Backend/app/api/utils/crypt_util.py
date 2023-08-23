import requests
from . import constants
import os
from passlib.context import (
    CryptContext, )

from app.api.auth.models import Userr

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
RADIUS_BASE_URL = os.environ.get("RADIUS_BASE_URL")
ROOT_TOKEN = os.environ.get("ROOT_TOKEN")


def verify_password(plain_password, user: Userr):
    # Make an API call to verify password

    # Get plain password from radius server
    r = requests.get(
        f'{RADIUS_BASE_URL}/permanent-users/view-password.json?token={ROOT_TOKEN}&cloud_id={user.cloud_id}&user_id={user.id}'
    )

    if r.status_code == 200 and r.json()['value'] == plain_password:
        return True

    # return pwd_context.verify(plain_password, hashed_password)
    return False


def get_password_hash(password):
    return pwd_context.hash(password)
