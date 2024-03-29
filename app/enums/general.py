from enum import Enum


class TimeZoneEnum(str, Enum):
    UTC = "UTC"
    TAIPEI = "Asia/Taipei"


class ChangedPasswordLengthEnum(int, Enum):
    PasswordMinLength = 8
    PasswordMaxLength = 12
