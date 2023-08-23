# email_sender.py

import os
import aiosmtplib
from email.message import EmailMessage

my_email = "ezekieloluwadamy@gmail.com"
password = os.environ.get("secret_key")

class EmailSender:
    @staticmethod
    async def send_email(email, token):
        try:
            message = EmailMessage()
            message.set_content(f"Hi, there. You're about to reset your Password. Please, approve this action with this Token: {token} or call +2349064531233 if you suspect this to be suspicious.")
            message['Subject'] = "Your Token"
            message['From'] = my_email
            message['To'] = email

            async with aiosmtplib.SMTP('smtp.gmail.com', 587) as smtp:
                await smtp.login(my_email, password)
                await smtp.send_message(message)

            return True

        except Exception as e:
            return {'error': str(e)}
