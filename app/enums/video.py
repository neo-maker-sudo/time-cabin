from enum import Enum

class VideoTypeEnum(str, Enum):
    MP4 = "mp4"
    MP3 = "mp3"

    @classmethod
    def members_tuple(cls):
        return tuple(cls.__members__.values())


class VideoDestinationFolderEnum(str, Enum):
    MP4 = "mp4"
    M3U8 = "m3u8"
