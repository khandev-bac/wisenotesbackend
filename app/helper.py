import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse
from uuid import UUID

import jwt
from fastapi import HTTPException, Request, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from passlib.context import CryptContext

from app.config.app_config import getAppConfig
from app.config.imagekit_config import URL_ENDPOINT, imagekit
from app.models.token import TokenReturnValue, Tokens

hasher = CryptContext(schemes=["argon2"])

app_config = getAppConfig()


def hash_password(original_pass: str) -> str:
    return hasher.hash(original_pass)


def verify_hash_password(entered_pass: str, hashed_pss: str) -> bool:
    return hasher.verify(entered_pass, hashed_pss)


def create_token(user_id: str) -> Tokens:
    access_payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    refresh_payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }
    access_token = jwt.encode(
        access_payload, app_config.access_token_key, algorithm="HS256"
    )
    refresh_token = jwt.encode(
        refresh_payload, app_config.refresh_token_key, algorithm="HS256"
    )
    return Tokens(access_token=access_token, refresh_token=refresh_token)


def verify_access_token(access_token: str) -> TokenReturnValue:
    decoded_value = jwt.decode(
        access_token, app_config.access_token_key, algorithms="HS256"
    )
    return TokenReturnValue(user_id=decoded_value["user_id"])


def verify_refresh_token(refresh_token: str) -> TokenReturnValue:
    decoded_value = jwt.decode(
        refresh_token, app_config.refresh_token_key, algorithms="HS256"
    )
    return TokenReturnValue(user_id=decoded_value["user_id"])


async def get_current_user(req: Request) -> UUID:
    auth_header = req.headers.get("Authorization")

    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    try:
        scheme, token = auth_header.split(" ")
        if scheme.lower() != "bearer":
            raise ValueError("Invalid auth scheme")

        payload = verify_access_token(token)

        if not payload or not payload.user_id:
            raise ValueError("Invalid token payload")

        return UUID(payload.user_id)

    except Exception as e:
        print(f"error in get_current_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to authenticate",
        )


async def upload_file_to_imagekit(files: UploadFile):
    filename = f"{uuid.uuid4()}{files.filename}"

    def _upload():
        return imagekit.files.upload(file=files.file, file_name=filename)

    try:
        result = await run_in_threadpool(_upload)
        return result
    except Exception as e:
        print(f"uploading to imagekit failed {e}")
        raise


def extract_youtube_video_id(url: str) -> str | None:
    parsed = urlparse(url)

    # youtu.be/VIDEO_ID
    if parsed.netloc in ("youtu.be", "www.youtu.be"):
        return parsed.path.lstrip("/")

    # youtube.com/watch?v=VIDEO_ID
    if parsed.netloc in ("youtube.com", "www.youtube.com"):
        if parsed.path == "/watch":
            return parse_qs(parsed.query).get("v", [None])[0]
        if parsed.path.startswith("/shorts/"):
            return parsed.path.split("/")[2]
        if parsed.path.startswith("/embed/"):
            return parsed.path.split("/")[2]

    return None
