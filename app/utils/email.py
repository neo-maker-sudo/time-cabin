import ssl
import smtplib
import random
import threading
from abc import ABCMeta, abstractmethod
from email.mime.text import MIMEText
from app.config import setting
from app.exceptions.general import EmailEncryptSetupException
from app.utils.general import urlsafe_base64_encode, retrieve_today_datetime


class EmailBackend(object, metaclass=ABCMeta):
    _sub_type = "html"
    _charset = "utf-8"

    def __init__(self) -> None:
        self.host = setting.EMAIL_HOST
        self.port = setting.EMAIL_PORT
        self.username = setting.EMAIL_HOST_USER
        self.password = setting.EMAIL_HOST_PASSWORD
        self.use_tls = setting.EMAIL_USE_TLS
        self.use_ssl = setting.EMAIL_USE_SSL
        self.timeout = setting.EMAIL_TIMEOUT
        self.ssl_keyfile = setting.EMAIL_SSL_KEYFILE
        self.ssl_certfile = setting.EMAIL_SSL_CERTFILE

        if self.use_ssl and self.use_tls:
            raise EmailEncryptSetupException

        self.connection = None
        self._lock = threading.RLock()

    @property
    def smtp_class(self):
        return smtplib.SMTP_SSL if self.use_ssl else smtplib.SMTP

    @property
    def ssl_context(self):
        if self.ssl_keyfile and self.ssl_certfile:
            ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_CLIENT)
            ssl_context.load_cert_chain(self.ssl_certfile, self.ssl_keyfile)
            return ssl_context

        return ssl.create_default_context()

    def open(self) -> bool:
        if self.connection:
            return False

        connection_params = {}

        if self.timeout is not None:
            connection_params["timeout"] = self.timeout

        if self.use_ssl:
            connection_params["context"] = self.ssl_context

        try:
            self.connection = self.smtp_class(
                self.host, self.port, **connection_params
            )

            if not self.use_ssl and self.use_tls:
                self.connection.starttls(context=self.ssl_context)

            if self.username and self.password:
                self.connection.login(self.username, self.password)

        except Exception as e:
            raise e

        return True

    def close(self):
        if self.connection is None:
            return

        try:
            self.connection.quit()

        except (ssl.SSLError, smtplib.SMTPServerDisconnected):
            self.connection.close()

        except smtplib.SMTPException as e:
            raise e

        finally:
            self.connection = None

    @abstractmethod
    def make_html_template(): pass

    @abstractmethod
    def write_mime_text(): pass

    @abstractmethod
    def write_email_body(): pass

    @abstractmethod
    def send_email(): pass


class ResetPasswordEmailBackend(EmailBackend):
    def make_html_template(self, email, b64, token):
        return setting.PASSWORD_RESET_HTML_TEMPLATE.substitute({
            "email": email,
            "datetime": retrieve_today_datetime(setting.DATE_TIME_FORMAT),
            "site_name": setting.SITE_NAME,
            "url": f"{setting.FRONT_END_DOMAIN}/{setting.PASSWORD_RESET_FRONT_END_ROUTE}/{b64}/{token}"
        })

    def write_mime_text(self, body):
        msg = MIMEText(
            body,
            self._sub_type,
            self._charset,
        )

        msg['Subject'] = setting.PASSWORD_RESET_EMAIL_SUBJECT
        msg['From'] = setting.SEND_EMAIL_FROM
        msg['To'] = setting.SEND_EMAIL_TO

        return msg

    def write_email_body(self, email, b64, token):
        body = self.make_html_template(email, b64, token)

        msg = self.write_mime_text(body)
        return msg.as_string()

    def send_email(self, token, user_id, email):
        b64 = urlsafe_base64_encode(user_id)

        new_connection = None

        with self._lock:
            try:
                new_connection = self.open()

                if not new_connection or new_connection is None:
                    return

                msg_string = self.write_email_body(email, b64, token)

                self.connection.sendmail(
                    setting.PROJECT_OWNER_EMAIL, email, msg_string
                )

            finally:
                if new_connection:
                    self.close()

class UserVerifyEmailBackend(EmailBackend):
    def make_html_template(self, email, code):
        return setting.USER_VERIFICATION_HTML_TEMPLATE.substitute({
            "email": email,
            "datetime": retrieve_today_datetime(setting.DATE_TIME_FORMAT),
            "site_name": setting.SITE_NAME,
            "code": code
        })

    def write_mime_text(self, body):
        msg = MIMEText(
            body,
            self._sub_type,
            self._charset,
        )

        msg['Subject'] = setting.USER_VERIFICATION_EMAIL_SUBJECT
        msg['From'] = setting.SEND_EMAIL_FROM
        msg['To'] = setting.SEND_EMAIL_TO

        return msg

    def write_email_body(self, email, code):
        body = self.make_html_template(email, code)

        msg = self.write_mime_text(body)
        return msg.as_string()

    def send_email(self, email, code):
        new_connection = None

        with self._lock:
            try:
                new_connection = self.open()

                if not new_connection or new_connection is None:
                    return

                msg_string = self.write_email_body(email, code)

                self.connection.sendmail(
                    setting.PROJECT_OWNER_EMAIL, email, msg_string
                )

            finally:
                if new_connection:
                    self.close()

    def generate_otp_code(self, length: int = setting.USER_VERIFICATION_EMAIL_CODE_LENGTH):
        try:
            otp_code = random.randrange(int("1" * length), int("9" * length))

        # cause ValueError if argument isn't integer or range problem, Ex:1,1
        except Exception as e:
            raise e

        return otp_code

reset_password_email_backend = ResetPasswordEmailBackend()
user_verify_email_backend = UserVerifyEmailBackend()