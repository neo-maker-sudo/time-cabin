from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.contrib.postgres.indexes import GinIndex
from app.config import setting
from app.enums.video import VideoTypeCreateEnum
from app.exceptions.videos import VideoNameFieldMaxLengthException


class Videos(models.Model):
    id = fields.IntField(pk=True)
    information = fields.TextField(default="")
    type = fields.CharEnumField(enum_type=VideoTypeCreateEnum, max_length=setting.VIDEO_TYPE_FIELD_MAX_LENGTH, null=True)
    url = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    likes = fields.IntField(default=0)
    label = fields.JSONField(null=True)

    user = fields.ForeignKeyField("models.Users", related_name="videos", null=True)

    class Meta:
        indexes = [
            GinIndex(fields={"label",})
        ]


    def __str__(self):
        return self.id

video_pydantic = pydantic_model_creator(Videos, name="video")
mainpage_pydantic = pydantic_model_creator(
    Videos,
    name="mainPage",
    exclude=(
        "user_id",
        "id",
        "type"
        "modified_at",
    )
)
video_update_pydantic = pydantic_model_creator(
    Videos,
    name="videoUpdate",
    exclude=(
        "id",
        "created_at",
        "modified_at",
        "url",
        "type",
        "likes",
    )
)
video_out_pydantic = pydantic_model_creator(Videos, name="video_in", exclude_readonly=True)