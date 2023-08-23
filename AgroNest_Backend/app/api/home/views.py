import datetime
import random
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from . import schemas, crud
from core.engine import get_db
from . import quotes
from .. import deps
from ..common.models import ResponseModel

router = APIRouter()

@router.post("/emotions")
async def post_emotion(emotion: str):
    """
    Post a variety of emotions, and get a Quote as a response
    Emotions can be either of these:
    [happy, sober, defeated, angry, confused]
    """
    if emotion == "happy":
        return (quotes.happy[random.randint(0, 2)])
    elif emotion == "sober":
        return (quotes.sober[random.randint(0, 2)])
    elif emotion == "defeated":
        return (quotes.defeated[random.randint(0, 2)])
    elif emotion == "angry":
        return (quotes.angry[random.randint(0, 2)])
    elif emotion == "confused":
        return (quotes.confused[random.randint(0, 2)])
    else:
        return {"message": "Invalid emotion"}

