from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from app.config import setting
from .video import Videos
from .general import FileField


class Users(models.Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=setting.USER_EMAIL_FIELD_MAX_LENGTH, unique=True, null=False)
    nickname = fields.CharField(max_length=setting.USER_NICKNAME_FIELD_MAX_LENGTH, null=True)
    active = fields.BooleanField(default=True)
    start_time = fields.DatetimeField(null=True)
    end_time = fields.DatetimeField(null=True)
    avatar = FileField(upload_to=setting.AVATAR_UPLOAD_TO, null=True)
    password = fields.CharField(max_length=setting.USER_PASSWORD_FIELD_MAX_LENGTH, null=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    videos: fields.ReverseRelation["Videos"]

    async def _pre_save(self, using_db, update_fields):
        if self.avatar is None:
            self.avatar = "{}{}".format(
                setting.STATIC_URL["public"],
                "default.png"
            )

        return await super()._pre_save(using_db, update_fields)

    def __str__(self):
        return self.email

    class PydanticMeta:
        exclude = ["password"]


users_pydantic = pydantic_model_creator(Users, name="users")
user_update_pydantic = pydantic_model_creator(
    Users,
    name="userUpdate",
    exclude=(
        "created_at",
        "modified_at",
        "start_time",
        "end_time",
        "active",
        "avatar",
        "email",
    )
)
user_avatar_pydantic = pydantic_model_creator(
    Users,
    name="userAvatar",
    exclude=(
        "created_at",
        "modified_at",
        "start_time",
        "end_time",
        "active",
        "email",
        "nickname",
    )
)
users_videos_pydantic = pydantic_model_creator(
    Users,
    name="userVideos",
    exclude=(
        "created_at",
        "modified_at",
        "start_time",
        "end_time",
        "active",
        "avatar",
        "nickname",
    )
)
users_out_pydantic = pydantic_model_creator(Users, name="users_in", exclude_readonly=True)
