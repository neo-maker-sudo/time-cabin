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


def upload_to_s3(source: str, cloud_folder: str, bucket: str) -> None:
    for file in glob.glob(f"{source}/*"):
        p_path = Path(file)
        try:
            setting.S3_CLIENT.upload_file(
                file,
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
