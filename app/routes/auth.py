from fastapi import APIRouter
from app.exceptions.auth import LoginInvalidException
from app.exceptions.general import InstanceDoesNotExistException
from app.utils.security import generate_access_token, verify_password
from app.sql.crud.auth import retrieve_user_by_email
from app.sql.schemas.auth import LoginSchemaIn, LoginSchemaOut


router = APIRouter(
    prefix="/api",
    tags=["auth"]
)


@router.post("/login", response_model=LoginSchemaOut)
async def login_view(schema: LoginSchemaIn):
    try:
        user = await retrieve_user_by_email(schema.email)

    except InstanceDoesNotExistException as exc:
        raise exc.raise_http_exception()

    if not verify_password(schema.password, user.password):
        raise LoginInvalidException.raise_http_exception()


    return {
        "access_token": generate_access_token({"user_id": user.id}),
        "token_type": "Bearer",
    }
