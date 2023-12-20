from fastapi import APIRouter, Depends, Response, status
from starlette.requests import Request
from app.config import setting
from app.exceptions.auth import (
    LoginInvalidException,
    AuthyUnregisteredException,
    AuthyVerifyException,
    AuthyConnectionException,
    OAuth2StateMismatchException,
    OAuth2AccessTokenInvalidGrantException,
    OAuth2UserInfoInvalidGrantException,
)
from app.exceptions.users import UserDoesNotExistException
from app.utils.auth.authy_client import verify_token, disable_registration, registration_status
from app.utils.auth.response import QrcodeResponse
from app.utils.auth.security import (
    verify_access_token,
    generate_access_token,
    verify_password,
    generate_2fa_qrcode,
)
from app import services
from app.repositories.database import PostgreSQLRepository
from app.services.auth import oauth2_service
from app.sql.crud.auth import retrieve_user_by_email_with_authy, update_user_last_login, create_authy, delete_authy
from app.sql.crud.users import retrieve_user_with_authy
from app.sql.schemas.auth import LoginSchemaIn, AuthyVerifySchemaIn, GoogleOauth2SchemaIn


router = APIRouter(
    prefix="/api",
    tags=["auth"]
)

@router.post("/login", status_code=status.HTTP_200_OK)
async def login_view(response: Response, schema: LoginSchemaIn):
    try:
        user = await retrieve_user_by_email_with_authy(schema.email)

    except LoginInvalidException as exc:
        raise exc.raise_http_exception()

    if not verify_password(schema.password, user.password):
        raise LoginInvalidException.raise_http_exception()

    await update_user_last_login(user)

    if user.authy is not None:
        response.status_code = status.HTTP_307_TEMPORARY_REDIRECT

    token_type, access_token, expires = generate_access_token({'user_id': str(user.id)})

    response.set_cookie(
        key=setting.COOKIE_ACCESS_TOKEN_KEY,
        value=f"{token_type} {access_token}",
        expires=expires,
        secure=setting.COOKIE_SECURE,
        httponly=setting.COOKIE_HTTPONLY,
        samesite=setting.COOKIE_SAMESITE,
    )

    return "OK"

@router.get("/2fa/qrcode")
async def generate_2fa_qrcode_view(
    user_id: int = Depends(verify_access_token),
):
    try:
        user = await retrieve_user_with_authy(user_id=user_id)

    except UserDoesNotExistException as exc:
        exc.raise_http_exception()

    qrcode_b64 = generate_2fa_qrcode(str(user.id), transfer_base64=True)
    return QrcodeResponse(
        content={
            "image": f"data:{QrcodeResponse.media_type} ;base64,{qrcode_b64}"
        }
    )

@router.post("/2fa/verify", status_code=status.HTTP_201_CREATED)
async def verify_2fa_view(
    response: Response,
    schema: AuthyVerifySchemaIn,
    user_id: int = Depends(verify_access_token),
):
    try:
        user = await retrieve_user_with_authy(user_id=user_id)

    except UserDoesNotExistException as exc:
        exc.raise_http_exception()

    try:
        if user.authy is None:
            status_content = registration_status(user_id)

            verify_token(
                user_authy_id=status_content["registration"]["authy_id"],
                token=schema.token,
            )

            # 確認沒問題加到 db
            await create_authy(
                authy_id=status_content["registration"]["authy_id"],
                user_id=user_id,
            )

        else:
            verify_token(
                user_authy_id=user.authy.authy_id,
                token=schema.token,
            )
            response.status_code = status.HTTP_200_OK

    except AuthyConnectionException as exc:
        raise exc.raise_http_exception()

    except AuthyUnregisteredException as exc:
        raise exc.raise_http_exception()

    except AuthyVerifyException as exc:
        raise exc.raise_http_exception()

    return "OK"

@router.delete("/2fa/disable", status_code=status.HTTP_204_NO_CONTENT)
async def disable_2fa_view(
    user_id: int = Depends(verify_access_token),
):
    try:
        user = await retrieve_user_with_authy(user_id=user_id)

    except UserDoesNotExistException as exc:
        exc.raise_http_exception()

    try:
        await delete_authy(user.authy)

        disable_registration(user_authy_id=user.authy.authy_id)

    except AuthyConnectionException as exc:
        raise exc.raise_http_exception()

    except AuthyUnregisteredException as exc:
        raise exc.raise_http_exception()

    return "OK"

@router.post("/google/login")
async def google_login_view(
    request: Request,
    response: Response,
    schema: GoogleOauth2SchemaIn,
):
    try:
        user_info, oauth_access_token, expires_in = await oauth2_service.login(
            "google",
            schema=schema,
            request=request,
        )

    except OAuth2StateMismatchException as exc:
        raise exc.raise_http_exception()

    except (OAuth2AccessTokenInvalidGrantException, OAuth2UserInfoInvalidGrantException) as exc:
        raise exc.raise_http_exception()

    user = await services.get_or_create_google_user(
        PostgreSQLRepository(),
        object={
            "email_verified": True,
            "email": user_info.get("email"),
            "nickname": user_info.get("name"),
            "avatar": user_info.get("picture")
        }
    )

    token_type, access_token = await services.storage_user_info(
        user,
        oauth_access_token=oauth_access_token,
        expires_in=expires_in,
        request=request
    )

    # 回傳自己產生的 token
    response.set_cookie(
        key=setting.COOKIE_ACCESS_TOKEN_KEY,
        value=f"{token_type} {access_token}",
        expires=expires_in,
        secure=setting.COOKIE_SECURE,
        httponly=setting.COOKIE_HTTPONLY,
        samesite=setting.COOKIE_SAMESITE,
    )

    return "OK"
