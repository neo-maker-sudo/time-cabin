import fnmatch
import glob
from pathlib import Path
from botocore.exceptions import (
    ClientError,
    ParamValidationError,
)
from app.config import setting
from app.exceptions.general import (
    AWSClientException,
    AWSParamValidationException,
    AWSLimitExceededException,
)


def download_s3_file(source: str, destination: str) -> None:
    try:
        setting.S3_CLIENT.download_file(
            setting.S3_BUCKET_NAME,
            source,
            destination,
        )

    except ClientError as e:
        raise AWSClientException

    except Exception as e:
        raise e


def upload_file_to_s3(upload_file, user_id: int) -> str:
    filename_folder = Path(upload_file.filename).stem
    
    try:
        setting.S3_CLIENT.upload_fileobj(
            upload_file.file,
            setting.S3_BUCKET_NAME,
            f"{user_id}/{filename_folder}/{upload_file.filename}",
            Config=setting.S3_TRANSFER_CONFIG
        )

    except ParamValidationError as e:
        raise AWSParamValidationException

    except ClientError as e:
        if e.response["Error"]["Code"] == "LimitExceededException":
            raise AWSLimitExceededException

        raise AWSClientException

    except Exception as e:
        raise e

    return filename_folder


def upload_to_s3(source: str, cloud_folder: str, bucket: str) -> None:
    for filepath in glob.glob(f"{source}/*"):
        if fnmatch.fnmatch(filepath, "*.ts") or fnmatch.fnmatch(filepath, "*.m3u8"):
            p_path = Path(filepath)
            try:
                setting.S3_CLIENT.upload_file(
                    filepath,
                    bucket,
                    f"{cloud_folder}/{p_path.stem}{p_path.suffix}",
                    Config=setting.S3_TRANSFER_CONFIG,
                )

            except ParamValidationError as e:
                raise AWSParamValidationException

            except ClientError as e:
                if e.response["Error"]["Code"] == "LimitExceededException":
                    raise AWSLimitExceededException

                raise AWSClientException

            except Exception as e:
                raise e
