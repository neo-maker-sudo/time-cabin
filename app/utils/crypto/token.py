from datetime import datetime
from app.config import setting
from app.utils.general import (
    integer_to_base36,
    base36_to_integer,
)
from app.utils.security import (
    salted_hmac,
    constant_time_compare
)


class PasswordResetTokenGenerator:
    salt = "app.utils.secuiry.PasswordResetTokenGenerator"
    _secret = None
    _algorithm = None

    def _get_secret(self):
        return self._secret or setting.PASSWORD_RESET_SECRET

    def _set_secret(self, secret):
        self._secret = secret

    secret = property(_get_secret, _set_secret)

    def _make_hash(self, user, timestamp):
        login_timestamp = (
            ""
            if user.last_login is None
            else user.last_login.replace(microsecond=0, tzinfo=None)
        )
        return f"{user.id}{timestamp}{login_timestamp}{user.email}"

    def _make_token_with_timestamp(self, user, timestamp, secret):
        ts_base36 = integer_to_base36(timestamp)

        hash = salted_hmac(
            self._make_hash(user, timestamp),
            self.salt,
            secret=secret,
            algorithm=self._algorithm,
        ).hexdigest()[::2]

        return "%s-%s" % (ts_base36, hash)

    def make_token(self, user):
        return self._make_token_with_timestamp(
            user,
            self.datetime_seconds(self._now()),
            self.secret
        )

    def verify_token(self, user, token):
        if not user and not token:
            return False

        try:
            ts_base36, _ = token.split("-")

        except ValueError:
            return False

        try:
            ts = base36_to_integer(ts_base36)

        except ValueError:
            return False
        
        # make sure timestamp has not been tamper with 
        if not constant_time_compare(
            self._make_token_with_timestamp(user, ts, self.secret),
            token
        ):
            return False

        if (self.datetime_seconds(self._now()) - ts) > setting.PASSWORD_RESET_TIMEOUT:
            return False

        return True

    def datetime_seconds(self, dt):
        return int(
            (dt - datetime(1970, 1, 1)).total_seconds()
        )

    def _now(self):
        return datetime.now()


token_generator = PasswordResetTokenGenerator()
