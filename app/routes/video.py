from fastapi import APIRouter, UploadFile, status, Depends, Form
from app.config import setting
from app.dependencies import verify_video_extension
from app.exceptions.videos import VideoDoesNotExistException
from app.enums.video import VideoTypeEnum
from app.sql.schemas.videos import (
    VideoCreateSchemaIn,
    VideoCreateSchemaOut,
    VideoUpdateSchemaIn,
    VideoUpdateSchemaOut,
)
from app.sql.crud.video import (
    retrieve_video,
    retrieve_videos,
    create_video,
    update_video,
    delete_video,
)
from app.utils.cloud import upload_to_s3
from app.utils.general import download_upload_file, save_tmp_folder
from app.utils.security import verify_access_token
from app.utils.video import mp4_to_m3u8


router = APIRouter(
    prefix="/api",
    tags=["videos"],
)


@router.get("/{video_id}/video")
async def retrieve_single_mp4_video_view(
    video_id: int,
    user_id: int = Depends(verify_access_token),
):
    try:
        video = await retrieve_video(video_id=video_id)

    except VideoDoesNotExistException as exc:
        raise exc.raise_http_exception()

    return video


@router.get("/videos")
async def retrieve_all_mp4_video_view(user_id: int = Depends(verify_access_token),):
    return await retrieve_videos()


@router.post("/create/video", status_code=status.HTTP_201_CREATED, response_model=VideoCreateSchemaOut)
async def create_mp4_video_view(
    upload_file: UploadFile = Depends(verify_video_extension),
    name: str = Form(..., max_length=64),
    information: str = Form(""),
    user_id: int = Depends(verify_access_token),
):
    # download upload_file to local
    # https://stackoverflow.com/questions/63580229/how-to-save-uploadfile-in-fastapi
    filename, tmp_video_path = download_upload_file(
        upload_file=upload_file,
        destination=setting.MP4_DESTINATION_FOLDER,
    )

    # save into database
    schema = VideoCreateSchemaIn(
        name=name,
        information=information,
        url=f"{setting.S3_BASE_URL}/{upload_file.filename}",
        type=VideoTypeEnum.MP4,
        user_id=user_id,
    )
    video = await create_video(create_object=schema.dict())

    with save_tmp_folder(destination=setting.M3U8_DESTINATION_FOLDER) as tmp_folder:
        mp4_to_m3u8(
            source=tmp_video_path.__str__(),
            filename=filename,
            destination=tmp_folder
        )

        upload_to_s3(source=tmp_folder, cloud_folder=filename, bucket=setting.S3_BUCKET_NAME)

    tmp_video_path.unlink()

    return video


@router.patch("/update/{video_id}/video", response_model=VideoUpdateSchemaOut)
async def update_mp4_video_view(
    video_id: int,
    schema: VideoUpdateSchemaIn,
    user_id: int = Depends(verify_access_token),
):
    video = await update_video(video_id, update_object=schema.dict())
    return video


@router.delete("/delete/{video_id}/video", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mp4_video_view(
    video_id: int,
    user_id: int = Depends(verify_access_token),
):
    try:
        await delete_video(video_id=video_id)

    except VideoDoesNotExistException as exc:
        raise exc.raise_http_exception()

    return "OK"
