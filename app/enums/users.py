from enum import Enum


class AvatarTypeEnum(str, Enum):
    JPG = "jpg"
    JPEG = "jpg"
    PNG = "png"

    @classmethod
    def members_tuple(cls):
        return tuple(cls.__members__.values())
