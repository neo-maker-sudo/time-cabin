from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from app.config import setting
from .general import FileField


class Users(models.Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True, null=False)
    nickname = fields.CharField(max_length=64, null=True)
    active = fields.BooleanField(default=True)
    start_time = fields.DatetimeField(null=True)
    end_time = fields.DatetimeField(null=True)
    avatar = FileField(upload_to=setting.AVATAR_UPLOAD_TO, null=True)
    password = fields.CharField(max_length=255, null=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    async def _pre_save(self, using_db, update_fields):
        if self.avatar is None:
            self.avatar = "{}{}".format(
                setting.STATIC_URL["public"],
                "default.png"
            )

        return await super()._pre_save(using_db, update_fields)

    def __str__(self):
        return self.email


users_pydantic = pydantic_model_creator(Users, name="users", exclude=("password",))
users_out_pydantic = pydantic_model_creator(Users, name="users_in", exclude_readonly=True)
