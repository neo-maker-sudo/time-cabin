import os
import boto3
from string import Template
from pathlib import Path
from oauthlib import oauth2
from app.enums.video import VideoDestinationFolderEnum


BASE_DIR = Path(__file__).parent.parent.parent

DOCKER_STATUS = os.getenv("DOCKER_STATUS")
FRONT_END_DOMAIN: str = "http://127.0.0.1:3000"
SITE_NAME: str = "NC 時光小屋"

DATABASE_URL: str = os.getenv("DATABASE_URL")
DATABASE_CONNECTION: str = "default"
DATABASE_MIGRATION_MODELS: list = [
    "app.sql.models.video",
    "app.sql.models.users",
]
REDIS_URL: str = os.getenv("REDIS_URL")
EMAIL_VERIFICATION_OTP_EXPIRED_SECONDS: int = 60 * 10
EMAIL_VERIFICATION_KEY_FORMAT_STRING: str = "emv-code-{}"

VIDEO_LABEL_FIELD_VIDEO_TAG_MIN_LENGTH: int = 1
VIDEO_LABEL_FIELD_VIDEO_TAG_MAX_LENGTH: int = 64
VIDEO_TYPE_FIELD_MAX_LENGTH: int = 10

USER_EMAIL_FIELD_MIN_LENGTH: int = 1
USER_EMAIL_FIELD_MAX_LENGTH: int = 255
USER_NICKNAME_FIELD_MIN_LENGTH: int = 1
USER_NICKNAME_FIELD_MAX_LENGTH: int = 64
USER_PASSWORD_FIELD_MIN_LENGTH: int = 1
USER_PASSWORD_FIELD_MAX_LENGTH: int = 255

S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME")
S3_REGION_NAME: str = os.getenv("S3_REGION_NAME")
S3_SERVICE_NAME: str = "s3"
S3_OFFICIAL_DOMAIN: str = "amazonaws.com"
S3_BASE_URL: str = "https://{0}.{1}.{2}.{3}".format(
    S3_BUCKET_NAME,
    S3_SERVICE_NAME,
    S3_REGION_NAME,
    S3_OFFICIAL_DOMAIN,
)

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

S3_CLIENT = boto3.client(
    S3_SERVICE_NAME,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

S3_TRANSFER_CONFIG = boto3.s3.transfer.TransferConfig(
    multipart_threshold=1024 * 25,  # 25 MB
    multipart_chunksize=1024 * 50,  # 50 MB
)

M3U8_DESTINATION_FOLDER = BASE_DIR / "static" / VideoDestinationFolderEnum.M3U8.value
MP4_DESTINATION_FOLDER = BASE_DIR / "static" / VideoDestinationFolderEnum.MP4.value

PASSWORD_REGEX: str = r"((?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,12})"

DATE_TIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"

JWT_ALGORITHM: str = "HS256"
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
JWT_EXPIRE_DAYS: int = 2

AVATAR_MAXIMUM_SIZE: int = 1024 * 1024 * 2

STATIC_URL = {
    "avatars": f"{S3_BASE_URL}/avatars",
    "public": f"{S3_BASE_URL}/public",
}

PASSWORD_RESET_SECRET: str = os.getenv("PASSWORD_RESET_SECRET")
PASSWORD_RESET_TIMEOUT: int = 60 * 10 # 10 minutes
PASSWORD_RESET_FRONT_END_ROUTE: str = "password/reset/confirm"

PROJECT_OWNER_EMAIL: str = "neochang@osensetech.com"

EMAIL_HOST: str = os.getenv("EMAIL_HOST")
EMAIL_PORT: int = 587
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS: bool = True
EMAIL_USE_SSL = None
EMAIL_TIMEOUT: int = 5
EMAIL_SSL_KEYFILE = None
EMAIL_SSL_CERTFILE = None

SEND_EMAIL_FROM: str = "Noreply <noreply@time-cabin.neochang.com>"
SEND_EMAIL_TO: str = "使用者"
PASSWORD_RESET_EMAIL_SUBJECT: str = '重設密碼信件'
PASSWORD_RESET_HTML_TEMPLATE = Template(
    Path(BASE_DIR / "app" / "templates" / "email" / "password_reset_email.html").read_text(encoding="utf-8")
)
USER_VERIFICATION_EMAIL_CODE_LENGTH: int = 8
USER_VERIFICATION_EMAIL_SUBJECT: str = '信箱驗證信件'
USER_VERIFICATION_HTML_TEMPLATE = Template(
    Path(BASE_DIR / "app" / "templates" / "email" / "user_verification_email.html").read_text(encoding="utf-8")
)

AUTHY_APPLICATION_NAME: str = os.getenv("AUTHY_APPLICATION_NAME")
AUTHY_APPLICATION_ID: str = os.getenv("AUTHY_APPLICATION_ID")
AUTHY_PRODUCTION_API_KEY: str = os.getenv("AUTHY_PRODUCTION_API_KEY")
AUTHY_QRCODE_JWT_TIMEDELTA: int = os.getenv("AUTHY_QRCODE_JWT_TIMEDELTA")
AUTHY_TOKEN_LENGTH: int = 8
AUTHY_TOKEN_REGEX: str = "[0-9]{8}"

MAINPAGE_PAGINATION_SIZE: int = 10

COOKIE_ACCESS_TOKEN_TYPE: str = "Bearer"
COOKIE_ACCESS_TOKEN_KEY: str = "tcat"
COOKIE_HTTPONLY: bool = True
COOKIE_SECURE: bool = True
COOKIE_SAMESITE: str = "lax"

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_SCOPE = "openid email profile"
GOOGLE_CALLBACK_ROUTE_NAME: str = "google_login_callback"
GOOGLE_OAUTH_CLIENT = oauth2.WebApplicationClient(GOOGLE_CLIENT_ID)
