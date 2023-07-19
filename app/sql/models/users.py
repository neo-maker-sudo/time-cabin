from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from .general import FileField


class Users(models.Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True, null=False)
    nickname = fields.CharField(max_length=64, null=True)
    active = fields.BooleanField(default=True)
    start_time = fields.DatetimeField(null=True)
    end_time = fields.DatetimeField(null=True)
    avatar = FileField(upload_to="static/avatar/", null=True)
    password = fields.CharField(max_length=255, null=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.email


users_pydantic = pydantic_model_creator(Users, name="users", exclude=("password",))
users_out_pydantic = pydantic_model_creator(Users, name="users_in", exclude_readonly=True)
