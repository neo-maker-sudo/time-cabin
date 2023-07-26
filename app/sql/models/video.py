
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from app.enums.video import VideoTypeEnum

class Videos(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=64)
    information = fields.TextField(default="")
    type = fields.CharEnumField(enum_type=VideoTypeEnum, max_length=10)
    url = fields.CharField(max_length=256)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    user = fields.ForeignKeyField("models.Users", related_name="videos", null=True)

    def __str__(self):
        return self.name

video_pydantic = pydantic_model_creator(Videos, name="video")
video_out_pydantic = pydantic_model_creator(Videos, name="video_in", exclude_readonly=True)