from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.notes_model import YoutubeLink

router = APIRouter(prefix="/note")

MAX_AUDIO_FILE_SIZE = 25 * 1024 * 1024


@router.get("/")
async def health():
    return {
        "message": "note endpoint is ok",
        "status_code": 200,
        "max_size": MAX_AUDIO_FILE_SIZE,
    }


@router.post("/audio")
async def upload_audio_file(audio: UploadFile = File(...)):
    try:
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
        # if len(contents) < MAX_AUDIO_FILE_SIZE:
        #     return JSONResponse(
        #         {"message": "file too small"},
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #     )

        return JSONResponse(
            {"message": f"file length:  {len(contents)}"},
            status_code=status.HTTP_200_OK,
        )

    except Exception as e:
        print(f"file upload failed: {e}")
        return JSONResponse(
            {"message": "failed to upload file"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/youtube-link")
async def paste_youtube_link(link: YoutubeLink):
    if not link.link.startswith("https://youtu.be") and not link.link.startswith(
        "https://www.youtube.com"
    ):
        return JSONResponse(
            {"message": "Invalid link please provide valid youtube link"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    video_id = link.link
    extract = video_id.split("/")[3].split("?")[0]
    is_watch_id = video_id.startswith("https://youtu.be")
    if is_watch_id:
        return {"message": "ok", "link": extract}
    else:
        watch_id = video_id.split("/")[3].split("?")[1].split("=")[1]
        return {"message": "ok", "link": watch_id}


@router.post("/docs")
async def upload_docs(docs: UploadFile = File(...)):
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
        return {
            "message": "docs uplpoad",
            "obj_key": obj_key,
            "file_type": docs.content_type,
        }
    except Exception as e:
        print(f"failed to upload {e}")
