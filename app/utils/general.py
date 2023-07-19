import shutil
from pytz import timezone
from datetime import datetime
from typing import Optional
from contextlib import contextmanager
from pathlib import Path, PosixPath
from tempfile import NamedTemporaryFile, SpooledTemporaryFile, TemporaryDirectory
from urllib.parse import urlencode, urlparse, urlunparse
from fastapi import UploadFile
from app.exceptions.general import ConvertDatetimeFormatException
from app.enums.general import TimeZoneEnum


def path_query_params(path, parmas: dict) -> str:
    parsed = list(urlparse(path.__str__()))
    parsed[4] = urlencode(parmas)
    return urlunparse(parsed)


@contextmanager
def save_tmp_file(destination: str, file: SpooledTemporaryFile, suffix: str, close_to_delete: bool = False) -> PosixPath:
    if not Path(destination).is_dir():
        Path(destination).mkdir(parents=True, exist_ok=True)

    # if global environment could not retrieve destination info, will be None as NamedTemporaryFile default value 
    with NamedTemporaryFile(dir=destination, suffix=suffix, delete=close_to_delete) as tmp_file:
        shutil.copyfileobj(file, tmp_file)
        yield tmp_file.name


@contextmanager
def save_tmp_folder(destination: str) -> str:
    if not Path(destination).is_dir():
        Path(destination).mkdir(parents=True, exist_ok=True)

    with TemporaryDirectory(dir=destination) as tmp_folder:
        yield tmp_folder


def download_upload_file(upload_file: UploadFile, destination: Optional[str] = None) -> tuple[str, PosixPath]:
    posix_path_file = Path(upload_file.filename)

    try:
        with save_tmp_file(
            destination=destination,
            file=upload_file.file,
            suffix=posix_path_file.suffix
        ) as tmp_filename:
            tmp_path = Path(tmp_filename)

    finally:
        upload_file.file.close()

    return posix_path_file.stem, tmp_path


def create_videos_folder(folders: list) -> None:
    try:
        for folder in folders:
            if not Path(folder).exists():
                Path(folder).mkdir()

    except Exception as e:
        raise e


def convert_datetime_format(utc_dt: datetime, format: str):
    if not isinstance(utc_dt, datetime) or utc_dt.tzinfo != timezone(TimeZoneEnum.UTC):
        raise ConvertDatetimeFormatException

    try:
        local_dt = utc_dt.astimezone(tz=timezone(TimeZoneEnum.TAIPEI)).strftime(format)

    except Exception as e:
        raise e

    return local_dt