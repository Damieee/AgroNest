from .models import Event  #ResponseSchema, ResponseModel
from ..auth.models import User
import logging
from fastapi import APIRouter, Depends

from core.engine import get_db
from ..utils.jwt_util import get_current_user

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/new")
async def create_event(
    new_event: Event,
    session=Depends(get_db),
    user: User = Depends(get_current_user)
) -> dict:

    print(user)
    session.add(new_event)
    session.commit()
    session.refresh(new_event)
    return {"message": "Event created successfully"}
