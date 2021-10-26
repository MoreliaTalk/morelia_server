from fastapi import Depends
from fastapi.applications import FastAPI
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

from starlette.responses import RedirectResponse
from . import login

app = FastAPI()

templates = Jinja2Templates(Path(__file__).parent / "templates")

app.include_router(login.router)


@app.exception_handler(login.NotLoginException)
def not_login_exception_handler(
        request: Request,
        exc: login.NotLoginException
        ):
    return RedirectResponse(url="/admin/login") 


@app.get("/login")
def login_admin(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/")
def index_admin(request: Request, user=Depends(login.login_manager)):
    return templates.TemplateResponse("index_admin.html", {"request": request})
