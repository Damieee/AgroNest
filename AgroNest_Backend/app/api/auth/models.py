from datetime import datetime
from typing import Any, List, Optional
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel
import uuid as uuid_pkg
from ..utils.crypt_util import get_password_hash 

from ..common.models import ResponseModel

class UserBase(SQLModel):
    email: EmailStr = Field(default='ezekieloluwadamy@gmail.com')
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    gender: str | None = None
    phone: str | None = None
    user_type: str = Field(default='farmer')
    status: bool = Field(default=False)  # Indicates if the user is online or not
    profile_photo_path: str | None = None
    cover_photo_path: str | None = None
    bio: str | None = None
    business_name: str | None = None
    created_at: datetime = Field(default=datetime.utcnow)
    follower_count: int = Field(default=0)
    following_count: int = Field(default=0)
    updated_at: datetime = Field(default=datetime.utcnow, onupdate=datetime.utcnow)


class User(UserBase, table=True):
    id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    hashed_password: str | None = None
    disabled: bool | None = False
    wallet: "Wallet" = Relationship(sa_relationship_kwargs={
        'uselist': False,
    }, )
    mobile_device_token: None | str = None


class Userr(UserBase, table=True):
    __tablename__: str = 'permanent_users'
    id: Optional[int] = Field(default=None, primary_key=True)
    cloud_id: str | None = None
    realm_id: str | None = None
    balance: int = 0
    to_date: datetime | None = None
    from_date: datetime | None = None
    profile: str
    profile_id: int
    address: str


class UserCreate(UserBase):
    password: str
    confirm_password: str  # field for password confirmation

    def update_password(self, new_password: str):
        self.hashed_password = get_password_hash(new_password)


class MobilePhoneToken(SQLModel):
    device_token: str


class UserRead(UserBase):
    id: int = Field(default='0')
    username: str | None = None
    disabled: bool | None = False


class Wallet(SQLModel, table=True):
    id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    balance: int = Field(default=0)
    active: bool = Field(default=True)
    updated_at: datetime = Field(default=datetime.utcnow())
    user_id: None | uuid_pkg.UUID = Field(
        default=None,
        foreign_key="user.id",
    )


class LoginRequest(SQLModel):
    identifier: EmailStr | str
    password: str


class Token(SQLModel):
    access_token: str = Field(
        default=
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMCIsImV4cCI6MTY3NDU4NTE3Nn0.jCEcE16vanjOc_rwp_JG5UdvBXj9F2j2tiZ286B3Fes'
    )
    token_type: str = Field(default='bearer')


class TokenData(SQLModel):
    user_id: str
