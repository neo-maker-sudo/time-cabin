import os
import boto3
from pathlib import Path
from app.enums.video import VideoDestinationFolderEnum

DATABASE_URL: str = os.getenv("DATABASE_URL")
DATABASE_MIGRATION_MODELS: list = [
    "app.sql.models.video",
]


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

M3U8_DESTINATION_FOLDER = Path(__file__).parent.parent.parent / VideoDestinationFolderEnum.M3U8.value
MP4_DESTINATION_FOLDER = Path(__file__).parent.parent.parent / VideoDestinationFolderEnum.MP4.value

