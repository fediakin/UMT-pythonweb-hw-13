"""
Сервіси для відправки електронних листів.
"""
import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr
from dotenv import load_dotenv

from app.core.security import create_email_token, create_reset_password_token

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", "test@test.com"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", "password"),
    MAIL_FROM=os.getenv("MAIL_FROM", "test@example.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 465)),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_FROM_NAME="Contacts App",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

async def send_email(email: EmailStr, host: str):
    """Відправляє лист для підтвердження електронної пошти."""
    try:
        token = create_email_token({"sub": email})
        html_content = f"""
        <html><body>
            <h2>Вітаємо!</h2>
            <p>Для підтвердження пошти перейдіть за посиланням:</p>
            <a href="{host}auth/verify/{token}">Підтвердити Email</a>
        </body></html>
        """
        message = MessageSchema(
            subject="Підтвердження Email",
            recipients=[email],
            body=html_content,
            subtype=MessageType.html
        )
        fm = FastMail(conf)
        await fm.send_message(message)
    except ConnectionErrors as err:
        print(f"Email error: {err}")

async def send_reset_password_email(email: EmailStr, host: str):
    """Відправляє лист із токеном для скидання пароля."""
    try:
        token = create_reset_password_token(email)
        html_content = f"""
        <html><body>
            <h2>Скидання пароля</h2>
            <p>Скопіюйте цей токен і використайте його для скидання пароля:</p>
            <b>{token}</b>
        </body></html>
        """
        message = MessageSchema(
            subject="Скидання пароля",
            recipients=[email],
            body=html_content,
            subtype=MessageType.html
        )
        fm = FastMail(conf)
        await fm.send_message(message)
    except ConnectionErrors as err:
        print(f"Email error: {err}")