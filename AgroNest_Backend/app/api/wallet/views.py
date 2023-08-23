from sqlmodel import select
from .models import Cards, ChargeCardRequest, FLWEventRequest, FundRequest, NewCard, PaystackEventRequest  #ResponseSchema, ResponseModel
from rave_python import Rave
from ..auth.models import Userr
import logging
import requests
from fastapi import APIRouter, Depends, Request
from ..utils import constants

from core.engine import get_db
from ..utils.jwt_util import get_current_user

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from paystackapp.api.paystack import Paystack
from paystackapp.api.transaction import Transaction

paystack = Paystack(secret_key=constants.PAYSTACK_SECRET_KEY)
import uuid
from datetime import datetime

# from deps import get_current_user

router = APIRouter()

logger = logging.getLogger(__name__)
rave = Rave(
    secretKey=constants.RAVE_LIVE_SECK_KEY,
    publicKey=constants.RAVE_LIVE_PUBK_KEY,
    usingEnv=False,
    # production=True,
)


def generate_reference_code():
    # Generate a unique identifier
    unique_id = str(uuid.uuid4().hex)[:6]

    # Get the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Combine the unique identifier and timestamp
    reference_code = f"{timestamp}-{unique_id}"

    print(reference_code)
    return reference_code


@router.post("/fund")
async def fund_wallet(
    fund_request: FundRequest,
    session=Depends(get_db),
    user: Userr = Depends(get_current_user)
) -> dict:

    return {
        "status": False,
        'message':
        'We are currently having challenges with our payment patners, kindly reach out to us at 08168706767 to make payment',
        'data': None,
    }

    # Collect customer information + amount
    # Initialize transaction
    # Verify Transaction or Handle Webhook

    # response = Transaction.verify(reference='n71fm6cp6m')
    tx_ref = generate_reference_code()

    payload = {
        'tx_ref': tx_ref,
        'amount': fund_request.amount,
        'currency': "NGN",
        'redirect_url': "https://portal.usefastlink.com/#/home",
        'meta': {
            'user_id': user.id,
        },
        'customer': {
            'email': user.email,
            'phonenumber': user.phone,
            'name': f"{user.name} {user.surname}"
        },
        # 'customizations': {
        #     'title':
        #     "Pied Piper Payments",
        #     'logo':
        #     "http://www.piedpiper.com/app/themes/joystick-v27/images/logo.png"
        # }
    }

    if fund_request.type == 'card':
        payload['payment_options'] = "card"

    response = requests.post(
        constants.RAVE_BASE_URL + '/payments',
        headers={
            'Authorization': f'Bearer {constants.RAVE_LIVE_SECK_KEY}',
        },
        json=payload,
    )

    # http://localhost:64006/#/fundWallet?reference=YOUR_REFERENCE

    response = response.json()

    if response['status'] == False:
        return {
            "status": False,
            'message': response['message'],
            'data': None,
        }

    return {
        "status": True,
        'message': response['message'],
        'data': {
            'link': response['data']['link'],
            'tx_ref': tx_ref,
        }
    }


@router.post("/verify_transaction")
async def verify_transaction(
    reference: str,
    session=Depends(get_db),
    user: Userr = Depends(get_current_user)
) -> dict:

    response = Transaction.verify(reference=reference)

    if response['data']['status'] == 'success':
        # Get amount from response
        # Credit wallet
        # Save authorization object

        return {
            "status": True,
            'message': 'Payment successful',
            'data': {
                'status': 'success'
            },
            # 'data': response['data']
        }

    return {
        "status": False,
        'message': 'Payment unsuccessful',
        'data': {
            'status': response['data']['status'],
            'reference': response['data']['reference']
        },
        # 'data': response['data']
    }


@router.get("/cards")
async def cards(
        session=Depends(get_db),
        user: Userr = Depends(get_current_user),
) -> dict:

    cards = session.exec(select(Cards).where(Cards.user_id == user.id)).all()

    return {
        "status": True,
        'message': 'Cards sucessfully fetched',
        'data': cards
    }


@router.delete("/cards/{card_id}")
async def delete_card(
        card_id: int,
        session=Depends(get_db),
        user: Userr = Depends(get_current_user),
) -> dict:

    card = session.exec(select(Cards).where(Cards.id == card_id)).one()

    session.delete(card)
    session.commit()

    return {
        "status": True,
        'message': 'Card sucessfully deleted',
        'data': None
    }


@router.post("/charge-card")
async def charge_card(
    request: ChargeCardRequest,
    session=Depends(get_db),
    user: Userr = Depends(get_current_user)
) -> dict:

    # Collect customer information + amount
    # Initialize transaction
    # Verify Transaction or Handle Webhook

    # response = Transaction.verify(reference='n71fm6cp6m')

    response = Transaction.charge(
        authorization_code=request.authorization_code,
        amount=request.amount * 100,
        email=request.email,
        callback_url='https://usefastlink.vercel.app/#/fundWallet',
    )
    # http://localhost:64006/#/fundWallet?reference=YOUR_REFERENCE

    if response['data']['status'] == 'success':

        # Get amount from response
        # Credit wallet
        # Save authorization object

        return {
            "status": True,
            'message': 'Successfully funded wallet',
            'data': None,
        }

    if response['status'] == False:
        return {
            "status": False,
            'message': response['message'],
            'data': None,
        }

    print(response)

    return {
        "status": False,
        'message': f"Payment failed, {response['data']['gateway_response']}",
        'data': None
    }


@router.post("/paystack_webhook/url")
async def paystack_webhook(
        body: PaystackEventRequest,
        session=Depends(get_db),
) -> dict:

    print(body.json())

    if body.event != "charge.success":
        return {
            "status": True,
            'message': 'Payment Successful',
        }

    response = body.data
    email = response['customer']['email']

    if response['status'] == 'success':
        # Get amount from response
        # Credit wallet
        # Save authorization object

        amount = response['amount'] / 100

        statement = select(Userr).where(Userr.email == email)
        results = session.exec(statement)
        fresh_user = results.one()

        # 2 times bonus
        amount = amount * 2

        fresh_user.balance = fresh_user.balance + amount
        session.add(fresh_user)
        session.commit()
        session.refresh(fresh_user)

        # Payment is successful, save authorization object
        authorization = response['authorization']
        signature = authorization['signature']

        if authorization['channel'] == 'card' and authorization[
                'reusable'] == True:

            statement = select(Cards).where(
                Cards.signature == signature,
                Cards.user_email == email,
            )

            results = session.exec(statement).first()

            # No previous card, add a new one
            if results is None:
                card = Cards(
                    **authorization,
                    user_id=fresh_user.id,
                    user_email=fresh_user.email,
                )
                session.add(card)
                session.commit()
            else:
                # There is a previous card, change authorization_code
                results.authorization_code = authorization[
                    'authorization_code']
                print('update')
                session.add(results)
                session.commit()

        return {
            "status": True,
            'message': 'Payment successful',
            'data': {
                'status': 'success'
            },
            # 'data': response['data']
        }

    return {
        "status": True,
        'message': 'Payment unsuccessful',
        'data': {
            'status': response['data']['status'],
            'reference': response['data']['reference']
        },
        # 'data': response['data']
    }


@router.post("/rave_webhook/url")
async def rave_webhook(
        body: FLWEventRequest,
        session=Depends(get_db),
) -> dict:

    print(body.json())

    if body.event != "charge.completed":
        return {
            "status": True,
            'message': 'Not an expected Payment',
        }

    response = body.data
    email = response['customer']['email']

    if response['status'] == 'successful':
        # Get amount from response
        # Credit wallet
        # Save authorization object

        amount = response['amount']

        statement = select(Userr).where(Userr.email == email)
        results = session.exec(statement)
        fresh_user = results.one()

        # 2 times bonus
        amount = amount * 2

        fresh_user.balance = fresh_user.balance + amount
        session.add(fresh_user)
        session.commit()
        session.refresh(fresh_user)

        # Flutterwave saves card automatically, and doesn't return token
        # # Payment is successful, save authorization object
        # authorization = response['authorization']
        # signature = authorization['signature']

        # if authorization['payment_type'] == 'card':

        #     statement = select(Cards).where(
        #         Cards.signature == signature,
        #         Cards.user_email == email,
        #     )

        #     results = session.exec(statement).first()

        #     # No previous card, add a new one
        #     if results is None:
        #         card = Cards(
        #             **authorization,
        #             user_id=fresh_user.id,
        #             user_email=fresh_user.email,
        #         )
        #         session.add(card)
        #         session.commit()
        #     else:
        #         # There is a previous card, change authorization_code
        #         results.authorization_code = authorization[
        #             'authorization_code']
        #         print('update')
        #         session.add(results)
        #         session.commit()

        return {
            "status": True,
            'message': 'Payment successful',
            'data': {
                'status': 'success'
            },
            # 'data': response['data']
        }

    return {
        "status": True,
        'message': 'Payment unsuccessful',
        'data': {
            'status': response['status'],
            'reference': response['tx_ref']
        },
        # 'data': response['data']
    }
