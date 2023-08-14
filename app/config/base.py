import os
import boto3
from string import Template
from pathlib import Path
from app.enums.video import VideoDestinationFolderEnum


BASE_DIR = Path(__file__).parent.parent.parent

DOCKER_STATUS = os.getenv("DOCKER_STATUS")
HOST_SCHEME: str = os.getenv("HOST_SCHEME")
HOST_NAME: str = os.getenv("HOST_NAME")
FRONT_END_DOMAIN: str = "http://127.0.0.1:3000"
SITE_NAME: str = "NC 時光小屋"

DATABASE_URL: str = os.getenv("DATABASE_URL")
DATABASE_MIGRATION_MODELS: list = [
    "app.sql.models.video",
    "app.sql.models.users",
]
VIDEO_NAME_FIELD_MIN_LENGTH: int = 1
VIDEO_NAME_FIELD_MAX_LENGTH: int = 64
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

AVATAR_UPLOAD_TO: str = "static/avatar/"
AVATAR_MAXIMUM_SIZE: int = 1024 * 1024 * 2
PUBLIC_UPLOAD_TO: str = "static/public/"

STATIC_URL = {
    "avatar": f"{HOST_SCHEME}://{HOST_NAME}/{AVATAR_UPLOAD_TO}",
    "public": f"{HOST_SCHEME}://{HOST_NAME}/{PUBLIC_UPLOAD_TO}",
}

PASSWORD_RESET_SECRET: str = os.getenv("PASSWORD_RESET_SECRET")
PASSWORD_RESET_TIMEOUT: int = 60 * 10 # 10 minutes
PASSWORD_RESET_FRONT_END_ROUTE: str = "password/reset/confirm"

PROJECT_OWNER_EMAIL: str = "neochang@osensetech.com"

EMAIL_HOST: str = "smtp.gmail.com"
EMAIL_PORT: int = 587
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS: bool = True
EMAIL_USE_SSL = None
EMAIL_TIMEOUT: int = 5
EMAIL_SSL_KEYFILE = None
EMAIL_SSL_CERTFILE = None

PASSWORD_RESET_EMAIL_SUBJECT: str = '重設密碼信件'
PASSWORD_RESET_EMAIL_FROM: str = "Neo Chang 的時光小屋網站"
PASSWORD_RESET_EMAIL_TO: str = "使用者"

PASSWORD_RESET_HTML_TEMPLATE = Template(
    Path(BASE_DIR / "app" / "templates" / "email" / "password_reset_email.html").read_text(encoding="utf-8")
)
