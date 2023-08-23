from typing import Optional
from ..auth.models import UserBase

class UserUpdate(UserBase):
    pass

class UserRead(UserBase):
    id: int


