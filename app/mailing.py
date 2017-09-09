# импорт
from flask import url_for, render_template
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

from app import app, mail
from .decorators import async
from config import SECRET_KEY, FLASK_MAIL_SENDER


# декоратор синхронной отправки письма
@async
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


# функция отправки почты
def send_email(subject, recipients, sender, html_body):
    msg = Message(subject, recipients=recipients, sender=sender)
    msg.html = html_body
    send_async_email(app, msg)


# функция отправки токена на почту
def send_confirmation_email(user_email):
    confirm_serializer = URLSafeTimedSerializer(SECRET_KEY)
    confirm_url = url_for(
        'confirm_email',
        token=confirm_serializer.dumps(user_email, salt='email-confirmation-salt'),
        _external=True)
    html = render_template('email/email_confirmation.html', confirm_url=confirm_url)
    send_email('Подтвердите свой email', [user_email], html_body=html, sender=FLASK_MAIL_SENDER)


# функция сброса пароля
def send_password_reset_email(user_email):
    password_reset_serializer = URLSafeTimedSerializer(SECRET_KEY)
    password_reset_url = url_for('reset_with_token',
        token=password_reset_serializer.dumps(user_email, salt='password-reset-salt'),
        _external=True)
    html = render_template('email/email_password_reset.html', password_reset_url=password_reset_url)
    send_email('Запрос на сброс пароля', [user_email], html_body=html, sender=FLASK_MAIL_SENDER)
