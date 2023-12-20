from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Playlist(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=32)
    videos: fields.ReverseRelation["Videos"]    

    class Meta:
        table = "playlists"

    def __str__(self):
        return self.id


class Videos(models.Model):
    id = fields.IntField(pk=True)
    identifier_code = fields.CharField(max_length=255)
    title = fields.TextField(default="")
    image = fields.TextField(default="")
    url = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    user = fields.ForeignKeyField("models.Users", related_name="videos", null=True)
    playlist = fields.ForeignKeyField("models.Playlist", related_name="videos", null=True)

    def __str__(self):
        return self.id

video_pydantic = pydantic_model_creator(Videos, name="video")
mainpage_pydantic = pydantic_model_creator(
    Videos,
    name="mainPage",
    exclude=(
        "user_id",
        "id",
    )
)
video_update_pydantic = pydantic_model_creator(
    Videos,
    name="videoUpdate",
    exclude=(
        "id",
        "created_at",
        "url",
    )
)
video_out_pydantic = pydantic_model_creator(Videos, name="video_in", exclude_readonly=True)