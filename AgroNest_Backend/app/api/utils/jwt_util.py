from datetime import (
    datetime,
    timedelta,
)
from typing import Any
from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapp.api.security import (
    OAuth2PasswordBearer, )

from jose import JWTError, jwt
from core.engine import get_db

from pydantic import (
    ValidationError, )
from sqlalchemy.ext.asyncio import (
    AsyncSession, )
from sqlmodel import Session

# from app.auth import (
#     crud, )
from app.api.auth.models import (TokenData, User)
from app.api.auth import (crud)

from .constants import (
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')


def create_access_token(
    *,
    data: dict,
    expires_delta: timedelta | None = None,
) -> dict[str, str]:
    try:
        payload = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=60)
        payload.update({"exp": expire})

        encoded_jwt_token = jwt.encode(
            payload,
            JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM,
        )
        return {"access_token": encoded_jwt_token, "token_type": "bearer"}
    except Exception:
        return {
            "message": "An error has occurred while generating an access"
            " token!"
        }


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
        id = payload.get("sub")
        print(id)
        if id is None:
            raise credentials_exception
        token_data = TokenData(user_id=id)
    except (JWTError, ValidationError) as ex:
        print(ex)
        raise credentials_exception

    user = await crud.find_existed_user(token_data.user_id, db)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
