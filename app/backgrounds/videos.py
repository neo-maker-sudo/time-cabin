import shutil
from pathlib import Path
from app.config import setting
from app.utils.cloud import upload_to_s3, download_s3_file
from app.utils.general import save_tmp_folder
from app.utils.video import mp4_to_m3u8
from app.sql.crud.users import insert_user_video


async def process_transcoding(folder: str, filename: str, filename_folder: str, video_id: int, user_id: int):
    if not Path(setting.MP4_DESTINATION_FOLDER / folder).exists():
        Path(setting.MP4_DESTINATION_FOLDER / folder).mkdir()

    # download s3 media
    download_s3_file(
        source=f"{folder}/{filename_folder}/{filename}",
        destination=setting.MP4_DESTINATION_FOLDER / folder / filename,
    )

    video_path = setting.MP4_DESTINATION_FOLDER / folder / filename

    # mkdir temperary folder and transcoding media object
    with save_tmp_folder(destination=setting.M3U8_DESTINATION_FOLDER) as tmp_folder:
        mp4_to_m3u8(
            source=video_path.__str__(),
            filename=filename_folder,
            destination=tmp_folder
        )

        # upload m3u8 object
        upload_to_s3(source=tmp_folder, cloud_folder=f"{folder}/{filename_folder}", bucket=setting.S3_BUCKET_NAME)

    shutil.rmtree(setting.MP4_DESTINATION_FOLDER / folder)

    update_object = {
        "type": "m3u8",
        "url": f"{setting.S3_BASE_URL}/{folder}/{filename_folder}/{filename_folder}.m3u8",
    }
    await insert_user_video(video_id, user_id, update_object)
