from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.config.app_config import getAppConfig
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
