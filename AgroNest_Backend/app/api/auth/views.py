# Import necessary modules and classes
from datetime import timedelta
import requests
from sqlmodel import Session

# Import constants, models, and utility functions
from app.api.utils.constants import ACCESS_TOKEN_EXPIRE_MINUTES
from .models import UserCreate, User, UserRead, LoginRequest, Token, Userr, MobilePhoneToken
from ..common.models import ResponseModel
import app.api.utils.constants as constants

# Import required modules for logging and FastAPI
import logging
from fastapi import APIRouter, Depends, HTTPException, status

# Import database session and utility functions
from core.engine import get_db
import app.api.utils.jwt_util as jwt_util

# Import cryptographic utility functions
from ..utils.crypt_util import get_password_hash, verify_password

# Import JWT utility functions
from ..utils.jwt_util import get_current_user

from ..utils.send_tokens import EmailSender
from ..utils.token_generator import TokenGenerator

# Import CRUD functions
from .crud import create_user, get_user

# Import OAuth2PasswordRequestForm for login form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
import asyncio

# Create an APIRouter instance
router = APIRouter()

# Create a logger instance
logger = logging.getLogger(__name__)

# Run the coroutine using an event loop
loop = asyncio.get_event_loop()
generated_token = loop.run_until_complete(TokenGenerator.generate_token())


# Endpoint to sign up a new user
@router.post(
    "/signup",
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK:
        ResponseModel.example(
            description='Signup Successful',
            data={
                'user': UserRead().dict(),
                'token': Token().dict()
            },
        ),
    },
)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if the user exists by email
    fetched_user = get_user(user.email, db)
    if fetched_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Check if passwords match
    if user.password != user.confirm_password:
        return ResponseModel.error(message="Passwords do not match")

    # Prepare payload for registration
    payload = {
        'login_page': 'AgroNest',
        'login_page_id': 20,
        'firstname': user.first_name,
        'lastname': user.last_name,
        'username': user.username,
        'password': user.password,
        'confirm_password': user.confirm_password,
        'phone': user.phone,
        'i18n': 'en_GB',
    }

    # Send registration request to external service
    r = requests.post(
        constants.RADIUS_BASE_URL + '/register-users/new-permanent-user.json',
        data=payload,
    )

    print(r.json())

    # Handle registration response
    if (r.json()['success'] != True):
        return ResponseModel.error(
            message=str(r.json()['message']),
            data=None,
        )

    # Return success response
    return ResponseModel.success(
        message='Signup successful. Continue to login in',
        data=None,
    )

# Endpoint to handle user login
@router.post(
    "/login",
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK:
        ResponseModel.example(
            description='Login Successful',
            data={
                'user': UserRead().dict(),
                'token': Token().dict()
            },
        ),
    },
)
async def login(
        request: LoginRequest,
        db: Session = Depends(get_db),
):

    # Authenticate user
    user = authenticate_user(request.identifier, request.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username, email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    token = create_access_token(user.id)
    return ResponseModel.success(
        message='Login successful',
        data={
            'user': user,
            'token': token,
        },
    )


# Endpoint to request password reset
@router.post(
    "/forgot_password",
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK:
        ResponseModel.example(
            description='Token sent Successfully',
            data={
                'user': UserRead().dict(),
                'token': Token().dict()
            },
        ),
    },
)

async def forgot_password(user: UserCreate, db: Session = Depends(get_db)):

    email = user.email

    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = generated_token # Generate a reset token

    # Send the token asynchronously
    email_sender = EmailSender()
    await email_sender.send_email(email, token) 

    return ResponseModel.success(message='Password reset instructions have been sent to your email', data=None)

# Endpoint to reset password
@router.post(
    "/reset_password", 
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK:
        ResponseModel.example(
            description='Password Reset Successful',
            data={
                'user': UserRead().dict(),
                'token': Token().dict()
            },
        ),
    },
)

async def reset_password(user: UserCreate, db: Session = Depends(get_db)):

    # Check if passwords match
    if user.password != user.confirm_password:
        return ResponseModel.error(message="Passwords do not match")

    # Prepare payload for reset
    payload = {
        'login_page': 'AgroNest',
        'reset_password_page_id': 21,
        'email': user.email,
        'token': generated_token,
        'password': user.password,
        'confirm_password': user.confirm_password,
        'phone': user.phone,
        'i18n': 'en_GB',
    }

    # Update user's password
    user.hashed_password = user.update_password(user.password)
    generated_token = None  # Reset the reset token
    db.commit()

    return ResponseModel.success(message='Password reset successful', data=None)



# Endpoint to fetch user information
@router.get(
    "/user",
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK:
        ResponseModel.example(
            description='User fetched successfully',
            data={
                'user': UserRead().dict(),
            },
        ),
    },
)
async def user(
        db: Session = Depends(get_db),
        user: Userr = Depends(get_current_user),
):

    # Fetch user data
    return ResponseModel.success(
        message='User fetched successfully',
        data=user,
    )

# Endpoint to get an access token
@router.post(
    "/token",
    include_in_schema=False,
    response_model=Token,
)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return create_access_token(user.id)


# Function to authenticate user
def authenticate_user(identifier: str, password: str, db: Session):
    user = get_user(identifier, db)
    if not user:
        return False
    if not verify_password(password, user):
        return False
    return user

# Function to create an access token
def create_access_token(id):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt_util.create_access_token(
        data={"sub": str(id)},
        expires_delta=access_token_expires,
    )
