from app.utils.email import reset_password_email_backend, user_verify_email_backend


async def send_reset_password_email(token, user_id, email):
    reset_password_email_backend.send_email(token, user_id, email)


async def send_user_verify_email(email, code):
    user_verify_email_backend.send_email(email, code)
