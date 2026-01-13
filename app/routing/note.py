import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from app.backgroundjob.tasks import example_task
from app.database.db import get_db
from app.database.schema.job_schema import Jobs, JobStatusEnum, JobTypeEnum
from app.database.schema.source_schema import Sources, SourceTypeEnum
from app.helper import (
    extract_youtube_video_id,
    get_current_user,
    upload_file_to_imagekit,
)
from app.models.notes_model import YoutubeLink

router = APIRouter(prefix="/note")

MAX_AUDIO_FILE_SIZE = 25 * 1024 * 1024


@router.post("/")
def health(content_id: str):
    try:
        job = example_task.delay(content_id)  # type: ignore[attr-defined]

        return {
            "message": "note endpoint is ok",
            "job_id": job.id,
            "status_code": 200,
            "max_size": MAX_AUDIO_FILE_SIZE,
        }
    except Exception as e:
        print(f"error in /: {e}")


@router.post("/audio")
async def upload_audio_file(
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    try:
        if not user_id:
            return JSONResponse(
                {"message": "Unauthorized"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        print("file uploading........")
        if audio.content_type is None:
            return JSONResponse(
                {"message": "Audio required"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if not audio.content_type.startswith("audio/"):
            return JSONResponse(
                {"message": "Invalid file"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        contents = await audio.read()
        if len(contents) > MAX_AUDIO_FILE_SIZE:
            return JSONResponse(
                {"message": "file too large"},
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            )

        file_upload_res = await upload_file_to_imagekit(files=audio)
        if len(contents) < MAX_AUDIO_FILE_SIZE:
            return JSONResponse(
                {"message": "file too small"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            # source data
        sourcedata = Sources(
            source_type=SourceTypeEnum.AUDIO,
            source_url=file_upload_res.url,
            source_name=audio.filename,
            size=file_upload_res.size,
            user_id=user_id,
        )
        db.add(sourcedata)
        db.commit()
        db.refresh(sourcedata)
        job = Jobs(
            source_id=sourcedata.id,
            job_type=JobTypeEnum.AUDIO,
            job_status=JobStatusEnum.QUEUED,
            progress=0,
            current_step="queued",
            retry_count=0,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return JSONResponse(
            {"message": "process queued", "job_id": job.id},
            status_code=status.HTTP_200_OK,
        )
        # Todo: audio file to celery
    except Exception as e:
        print(f"file upload failed: {e}")
        return JSONResponse(
            {"message": "failed to upload file"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/youtube-link")
async def paste_youtube_link(
    link: YoutubeLink,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    try:
        if not user_id:
            return JSONResponse(
                {"message": "Unauthorized"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        if not link.link.startswith("https://youtu.be") and not link.link.startswith(
            "https://www.youtube.com"
        ):
            return JSONResponse(
                {"message": "Invalid link please provide valid youtube link"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        video_id = extract_youtube_video_id(link.link)
        if not video_id:
            return JSONResponse(
                {"message": "Invalid YouTube link"},
                status_code=HTTP_400_BAD_REQUEST,
            )
        sourcedata = Sources(
            source_type=SourceTypeEnum.YOUTUBE,
            source_url=link.link,
            source_name=link.link,
            user_id=user_id,
        )
        db.add(sourcedata)
        db.commit()
        db.refresh(sourcedata)
        job = Jobs(
            source_id=sourcedata.id,
            job_type=JobTypeEnum.YOUTUBE,
            job_status=JobStatusEnum.QUEUED,
            progress=0,
            current_step="queued",
            retry_count=0,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        # processing in queue
        return {
            "message": "YouTube link accepted",
            "job_id": job.id,
            "video_id": link.link,
        }
    except Exception as e:
        return JSONResponse(
            {"message": "Failed to process this link"},
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/docs")
async def upload_docs(
    docs: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user),
):
    try:
        print("uploading documents...")

        if docs.content_type is None:
            return JSONResponse(
                {"message": "Document required"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if not docs.content_type.startswith("application/"):
            return JSONResponse(
                {"message": "Invalid document"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        obj_key = f"documents/{docs.filename}"
        file_upload = await upload_file_to_imagekit(files=docs)
        # TODO: to save in db
        sourcedata = Sources(
            source_type=SourceTypeEnum.DOCUMENTS,
            source_url=file_upload.url,
            source_name=docs.filename,
            user_id=user_id,
        )
        db.add(sourcedata)
        db.commit()
        db.refresh(sourcedata)
        job = Jobs(
            source_id=sourcedata.id,
            job_type=JobTypeEnum.DOCUMENTS,
            job_status=JobStatusEnum.QUEUED,
            progress=0,
            current_step="queued",
            retry_count=0,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return {
            "message": "docs uplpoad",
            "obj_key": obj_key,
            "file_type": docs.content_type,
        }
    except Exception as e:
        print(f"failed to upload {e}")
