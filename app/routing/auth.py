import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from firebase_admin.auth import verify_id_token
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from user_agents import parse

from app.database.db import get_db
from app.database.schema.user_schema import AuthProvider, Users
from app.helper import (
    create_token,
    hash_password,
    verify_access_token,
    verify_hash_password,
    verify_refresh_token,
)
from app.models.auth_model import GoogleAuth, RefreshTokenBody, SignIn, Signup

router = APIRouter(prefix="/auth")


@router.get("/")
def auth():
    return {"message": "this is auth router"}


@router.post("/signup")
def signup(request: Request, body: Signup, db: Annotated[Session, Depends(get_db)]):
    try:
        existingUser = db.query(Users).filter(Users.email == body.email).first()
        if existingUser:
            return JSONResponse(
                {"message": "User email is already exits"},
                status_code=status.HTTP_409_CONFLICT,
            )
        # user_agent_str = request.headers.get("user-agent", "")
        # user_agent = parse(user_agent_str)
        new_user = Users(
            email=body.email,
            password=hash_password(body.password),
            auth_provider=AuthProvider.EMAIL,
            # user_device=user_agent,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        tokens = create_token(str(new_user.id))
        return JSONResponse(
            content={
                "message": "Successfully user created",
                "tokens": tokens.model_dump(),
                "user": {
                    "user_id": str(new_user.id),
                    "email": new_user.email,
                    "auth_provider": new_user.auth_provider.value,
                    "plan": new_user.plan.value,
                    "created_at": new_user.created_at.isoformat(),
                },
            },
            status_code=status.HTTP_201_CREATED,
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user {e}",
        )


@router.post("/login")
def login(body: SignIn, db: Annotated[Session, Depends(get_db)]):
    try:
        existingUser = db.query(Users).filter(Users.email == body.email).first()
        if not existingUser:
            return JSONResponse(
                {"message": "User not found with this email"},
                status_code=status.HTTP_404_NOT_FOUND,
            )
        isValidPassword = verify_hash_password(
            body.password, str(existingUser.password)
        )
        if not isValidPassword:
            return JSONResponse(
                {"message": "Invalid email or password"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        tokens = create_token(str(existingUser.id))
        return JSONResponse(
            content={
                "message": "Successfully loggedIn",
                "tokens": tokens.model_dump(),
                "user": {
                    "user_id": str(existingUser.id),
                    "email": existingUser.email,
                    "auth_provider": existingUser.auth_provider.value,
                    "plan": existingUser.plan.value,
                    "created_at": existingUser.created_at.isoformat(),
                },
            },
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to login {e}",
        )


@router.post("/google")
def google_auth(body: GoogleAuth, db: Annotated[Session, Depends(get_db)]):
    try:
        payload_from_firebase = verify_id_token(body.idToken)
        print(
            f"firebase user data: {payload_from_firebase}",
        )
        email = payload_from_firebase.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not available from Google account",
            )
        user = db.query(Users).filter(Users.email == email).first()
        if not user:
            user = Users(
                email=email,
                google_id=payload_from_firebase["uid"],
                auth_provider="google",
                profile_img=payload_from_firebase.get("picture"),
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        tokens = create_token(str(user.id))
        return JSONResponse(
            {"message": "Google login successful", "token": tokens.model_dump()},
            status_code=status.HTTP_200_OK,
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google login failed",
        )


@router.post("/refresh")
def refresh_token(body: RefreshTokenBody, db: Annotated[Session, Depends(get_db)]):
    try:
        decode_refresh_token = verify_refresh_token(refresh_token=body.refresh_token)
        if not decode_refresh_token:
            return JSONResponse(
                {"message": "refreshed failed"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        user_id = decode_refresh_token.user_id
        tokens = create_token(user_id)
        return JSONResponse(
            {"message": "ok", "tokens": tokens.model_dump()},
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        print(f"failed to get new tokens: {e}")
        return JSONResponse(
            {
                "message": "failed",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/test")
def testToken():
    userid = uuid.uuid4()
    tokens = create_token(str(userid))
    refreshtoken = tokens.refresh_token
    verified_ref = verify_refresh_token(refreshtoken)
    return {
        "user_id": str(userid),
        "access_token": refreshtoken,
        "verified_user_id": verified_ref.user_id,
    }
