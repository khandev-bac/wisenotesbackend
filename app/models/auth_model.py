from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class GoogleAuth(BaseModel):
    idToken: str


class Signup(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=12)


class SignIn(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=12)
