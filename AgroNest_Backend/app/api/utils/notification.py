import json
from pathlib import Path
from fastapi import HTTPException, status

import firebase_admin
from firebase_admin import credentials, messaging


def init_fcm():
    if not len(firebase_admin._apps):
        cred = credentials.Certificate(
            "backend/app/api/utils/AgroNest-firebase-adminsdk.json"
        )
        firebase_admin.initialize_app(cred)


class FCM(object):

    @staticmethod
    def notify(token, title, body, data=None):
        # message = messaging.Message(
        #     notification=messaging.Notification(title=title, body=body),
        #     token=token,
        #     data=payload,
        # )

        # See documentation on defining a message payload.
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data,
            token=token,
        )

        # Send a message to the device corresponding to the provided
        # registration token.
        try:
            print(message.__dict__)
            messaging.send(message)
        except (Exception) as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error, check back later",
                headers={"WWW-Authenticate": "Bearer"},
            )
