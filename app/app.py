from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.routing import auth, note, user

app = FastAPI()


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )


app_v1 = APIRouter(prefix="/v1/api")
app_v1.include_router(auth.router)
app_v1.include_router(user.router)
app_v1.include_router(note.router)


@app_v1.get("/", tags=["root"])
def read_root():
    return {"Hello": "World"}


app.include_router(app_v1)
