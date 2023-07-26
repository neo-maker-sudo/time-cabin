import io
import uuid
from pathlib import Path
from typing import Any
from tortoise import fields, ConfigurationError
from tortoise.models import Model
from starlette.datastructures import UploadFile
from app.config import setting


class FileField(fields.TextField):
    def __init__(self, upload_to: str, **kwargs) -> None:
        super().__init__(**kwargs)

        if not isinstance(upload_to, str):
            raise ConfigurationError(
                "upload_to argument isn't str data type: {}({})".format(
                    upload_to, type(upload_to)
                )
            )

        if not Path(setting.BASE_DIR / upload_to).exists():
            Path(setting.BASE_DIR / upload_to).mkdir(parents=True)

        self.upload_to = upload_to

    def is_binary_stream(self, upload_file: UploadFile) -> bool:
        return isinstance(upload_file.file._file, io.TextIOBase)

    def to_db_value(self, value: UploadFile,  instance: type[Model] | Model) -> Any:
        if isinstance(value, UploadFile):
            is_binary = self.is_binary_stream(value)

        elif value is None or value.startswith(setting.STATIC_URL["public"]):
            return super().to_db_value(value, instance)

        if Path(setting.BASE_DIR / self.upload_to / value.filename).is_file():
            locate_filename = f"{str(uuid.uuid4())}_{value.filename}"
        else:
            locate_filename = value.filename

        mode = "wb" if not is_binary else "w"
        path = (
            setting.BASE_DIR / self.upload_to / locate_filename
        ).__str__()

        with open(path, mode=mode) as file:
            file.write(value.file.read())

        return "{}{}".format(
            setting.STATIC_URL["avatar"],
            locate_filename
        )