"""sqlmodel.Session: This is a class from the SQLModel library used to manage database sessions.

User from ..auth.models: This is a model representing a user, likely imported from an authentication module.

firebase_admin and related modules: These are modules from the Firebase Admin SDK used to interact with Firebase services, particularly Firebase Cloud Messaging (FCM) for notifications.

ResponseModel from ..common.models: This is a model representing a response, probably containing a message and data.

logging: The standard Python logging module for handling log messages.

fastapi.api.APIRouter: This is a class that helps organize and define routes within a FastAPI application.

core.engine.get_db: A function used to obtain a database session.

Various functions from different crud and utils modules."""


from sqlmodel import Session
from ..auth.models import User

import firebase_admin
from firebase_admin import credentials, messaging

# from .models import Event  #ResponseSchema, ResponseModel

from ..common.models import ResponseModel

import logging
from fastapi import APIRouter, Depends, HTTPException, status

from core.engine import get_db

from .crud import (
    update_wallet,
    get_wallet,
)

from ..auth.crud import (
    find_existed_user, )

from ..utils.jwt_util import get_current_user
from ..utils.notification import FCM

router = APIRouter()

# logger = logging.getLogger(__name__)

# raise HTTPException(
#     status_code=status.HTTP_400_BAD_REQUEST,
#     detail="Email already exists",
#     headers={"WWW-Authenticate": "Bearer"},
# )

# This route is used for charging one wallet and crediting another wallet. It involves transferring a certain amount from one wallet to another.
@router.get(
    "/charge/{wallet_id}",
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK:
        ResponseModel.example(
            description='Payment Successful',
            data={
                'user': 'UserRead().dict()',
                'token': 'Token().dict()'
            },
        ),
    },
)

# This handler checks if the given wallet_id is valid and if the balance is sufficient in the sender's wallet.
# It subtracts the specified amount from the sender's wallet and adds it to the recipient's wallet.
# It sends notifications to both parties 

async def charge(
    wallet_id: str,
    amount: int,
    db=Depends(get_db),
    user: User = Depends(get_current_user)
) -> dict:

    # Check if wallet is not the user wallet
    # Check if balance is sufficient
    # Check if wallet_id is valid
    # Subtract money from from_wallet, and add to to_wallet
    # Send notification to parties
    # return a success response

    # Check if wallet_id is valid
    from_wallet = get_wallet(wallet_id, db)
    if from_wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet Id is not valid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if balance is sufficient
    if from_wallet.balance <= amount:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insufficient balance for transaction",
            headers={"WWW-Authenticate": "Bearer"},
        )

    to_wallet = user.wallet

    # Subtract money from current wallet, and add to the other wallet
    from_wallet.balance -= amount
    to_wallet.balance += amount
    from_wallet = update_wallet(from_wallet, db)
    update_wallet(to_wallet, db)

    from_user = await find_existed_user(str(from_wallet.user_id), db=db)
    if from_user:
        FCM.notify(
            token=user.mobile_device_token,
            title='Debit Alert',
            body=f'You just got debited with NGN{amount} from your wallet',
            data={'wallet': str(from_user.wallet.json())},
        )

    #Get info about to_wallet user
    to_user = await find_existed_user(str(to_wallet.user_id), db=db)
    if to_user:
        FCM.notify(
            token=to_user.mobile_device_token,
            title='Credit Alert',
            body=f'You just got credited with NGN{amount} in your wallet',
            data={'wallet': str(to_user.wallet.json())},
        )

    # Send notification to parties
    # return a success response

    # print(user)
    # session.add(new_event)
    # session.commit()
    # session.refresh(new_event)

    return ResponseModel.success(
        message='Charge Successful',
        data=to_wallet,
    )

# Similar to the /charge route, this route also transfers a certain amount from the user's wallet to another wallet.
@router.post(
    "/pay/{wallet_id}",
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK:
        ResponseModel.example(
            description='Payment Successful',
            data={
                'user': 'UserRead().dict()',
                'token': 'Token().dict()'
            },
        ),
    },
)

#  This handler checks if the user's wallet has sufficient balance.
# It subtracts the specified amount from the user's wallet and adds it to the recipient's wallet.
# It sends notifications to both parties. 

async def pay(
    wallet_id: str,
    amount: int,
    db=Depends(get_db),
    user: User = Depends(get_current_user)
) -> dict:

    # Check if wallet is not the user wallet
    # Check if balance is sufficient
    # Check if wallet_id is valid
    # Subtract money from from_wallet, and add to to_wallet
    # Send notification to parties
    # return a success response

    # Mobile app should fetch latest balance from db

    # Check if balance is sufficient
    from_wallet = user.wallet
    if from_wallet.balance <= amount:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insufficient balance for transaction",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if wallet_id is valid
    to_wallet = get_wallet(wallet_id, db)
    if to_wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet Id is not valid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Subtract money from curent wallet, and add to the other wallet
    from_wallet.balance -= amount
    to_wallet.balance += amount
    from_wallet = update_wallet(from_wallet, db)
    update_wallet(to_wallet, db)

    from_user = await find_existed_user(str(from_wallet.user_id), db=db)
    if from_user:
        FCM.notify(
            token=user.mobile_device_token,
            title='Debit Alert',
            body=f'You just got debited with NGN{amount} from your wallet',
            data={'wallet': str(from_user.wallet.json())},
        )

    #Get info about to_wallet user
    to_user = await find_existed_user(str(to_wallet.user_id), db=db)
    if to_user:
        FCM.notify(
            token=to_user.mobile_device_token,
            title='Credit Alert',
            body=f'You just got credited with NGN{amount} in your wallet',
            data={'wallet': str(to_user.wallet.json())},
        )

    # Send notification to parties
    # return a success response

    # print(user)
    # session.add(new_event)
    # session.commit()
    # session.refresh(new_event)

    return ResponseModel.success(
        message='Transaction Successful',
        data=from_wallet,
    )

# This route allows the user to add funds to their own wallet, effectively "topping up" their balance.
@router.post(
    "/top-up",
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK:
        ResponseModel.example(
            description='Payment Successful',
            data={
                'user': 'UserRead().dict()',
                'token': 'Token().dict()'
            },
        ),
    },
)

# This handler adds the specified amount to the user's wallet balance.
# It sends a notification to the user.

async def top_up(
    amount: int, db=Depends(get_db), user: User = Depends(get_current_user)
) -> dict:

    to_wallet = user.wallet

    # Subtract money from curent wallet, and add to the other wallet
    to_wallet.balance += amount

    update_wallet(to_wallet, db)
    FCM.notify(
        token=user.mobile_device_token,
        title='Credit Alert',
        body=f'You just got credited with NGN{amount} in your wallet',
        data={'wallet': str(user.wallet.json())},
    )
    # Send notification to parties
    # return a success response

    # print(user)
    # session.add(new_event)
    # session.commit()
    # session.refresh(new_event)

    return ResponseModel.success(
        message='Top-Up Successful',
        data=to_wallet,
    )

# This handler retrieves the current wallet balance of the authenticated user.
@router.get(
    "/wallet",
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK:
        ResponseModel.example(
            description='Payment Successful',
            data={
                'user': 'UserRead().dict()',
                'token': 'Token().dict()'
            },
        ),
    },
)
async def wallet(
        db=Depends(get_db),
        user: User = Depends(get_current_user),
) -> dict:

    # balance = user.wallet.balance

    # Send notification to parties
    # return a success response

    # print(user)
    # session.add(new_event)
    # session.commit()
    # session.refresh(new_event)

    return ResponseModel.success(
        message='Successful',
        data=user.wallet,
    )

# This route sends a notification to the authenticated user's mobile device, informing them about a credit to their wallet.
@router.get(
    "/notify",
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK:
        ResponseModel.example(
            description='Payment Successful',
            data={
                'user': 'UserRead().dict()',
                'token': 'Token().dict()'
            },
        ),
    },
)
async def notify(
        user: User = Depends(get_current_user),
        db=Depends(get_db),
) -> dict:
    FCM.notify(
        token=user.mobile_device_token,
        title='Credit Alert',
        body='You just got credited with NGN200 in your wallet',
        data={'wallet': str(user.wallet.json())},
    )

    registration_token = 'duumM8AFRvKO3uweAXR3iF:APA91bEx-vbOSIqdqNWwGbWdXLizpdJl-IsreTWkw8pIuz52ue2sZqPYGFhAAH-3j09lh06M8TCL_GQTohDTMA_ktBWuyfoDmy8ZvJf8k-diiUc7lQvGfpr8QJZQvgzfSip0SZy__udl'

    return ResponseModel.success(
        message='Successful Sent message',
        data=None,
    )

