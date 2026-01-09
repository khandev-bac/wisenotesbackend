from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.status import HTTP_200_OK
from user_agents import parse

from app.database.db import get_db
from app.database.schema.user_schema import AuthProvider, Users
from app.helper import create_token, hash_password, verify_hash_password
from app.models.auth_model import GoogleAuth, SignIn, Signup

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
                status_code=status.HTTP_302_FOUND,
            )
        # user_agent_str = request.headers.get("user-agent", "")
        # user_agent = parse(user_agent_str)
        new_user = Users(
            email=body.email,
            password=hash_password(body.password),
            auth_provider=AuthProvider.EMAIL,
            # user_device=user_agent,
        )
        tokens = create_token(str(new_user.id))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
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


# @router.post("/google")
# def google_auth(body:GoogleAuth,db:Annotated[Session,Depends(get_db)]):
#     try:
