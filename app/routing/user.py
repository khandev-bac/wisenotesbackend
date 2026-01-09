from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db

router = APIRouter(prefix="/user")


@router.get("/")
def auth(db: Annotated[Session, Depends(get_db)]):
    return {"message": "this is user router"}
