import ssl
import smtplib
import threading
from email.mime.text import MIMEText
from app.config import setting
from app.exceptions.general import EmailEncryptSetupException
from app.utils.general import urlsafe_base64_encode, retrieve_today_dateime


class EmailBackend:
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

    def _write_email_body(self, b64, token, email):
        # 產出 template
        body = setting.PASSWORD_RESET_HTML_TEMPLATE.substitute({
            "email": email,
            "datetime": retrieve_today_dateime(setting.DATE_TIME_FORMAT),
            "site_name": setting.SITE_NAME,
            "url": f"{setting.FRONT_END_DOMAIN}/{setting.PASSWORD_RESET_FRONT_END_ROUTE}/{b64}/{token}"
        })

        msg = MIMEText(
            body,
            self._sub_type,
            self._charset,
        )

        msg['Subject'] = setting.PASSWORD_RESET_EMAIL_SUBJECT
        msg['From'] = setting.PASSWORD_RESET_EMAIL_FROM
        msg['To'] = setting.PASSWORD_RESET_EMAIL_TO

        return msg.as_string()

    def send_mail(self, token, user):
        b64 = urlsafe_base64_encode(user.id)

        new_connection = None

        with self._lock:
            try:
                new_connection = self.open()

                if not new_connection or new_connection is None:
                    return

                msg_string = self._write_email_body(b64, token, user.email)

                self.connection.sendmail(
                    setting.PROJECT_OWNER_EMAIL, user.email, msg_string
                )

            finally:
                if new_connection:
                    self.close()


email_backend = EmailBackend()
