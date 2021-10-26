from fastapi import Depends
from fastapi.applications import FastAPI
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from pathlib import Path
from loguru import logger
import sqlobject as orm

from starlette.responses import RedirectResponse, Response

from mod import models
from . import login, logs

app = FastAPI()

templates = Jinja2Templates(Path(__file__).parent / "templates")

app.include_router(login.router)
app.include_router(logs.router)

try:
    db_connection = orm.connectionForURI(login.database.get("uri"))
except Exception as ERROR:
    logger.exception(str(ERROR))
finally:
    orm.sqlhub.processConnection = db_connection


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

@app.get("/status")
def status_admin(request: Request, user=Depends(login.login_manager)):
    Messages_count = models.Message.select().count()
    Flows_count = models.Flow.select().count()
    Users_count = models.UserConfig.select().count()

    return templates.TemplateResponse("status_admin.html", {
        "request": request,
        "Messages_count": Messages_count,
        "Flows_count": Flows_count,
        "Users_count": Users_count
    })


@app.get("/manage")
def manage_admin(request: Request, user=Depends(login.login_manager)):
    return templates.TemplateResponse("manage_admin.html", {"request": request})


@app.get("/logs")
def manage_logs(request: Request, user=Depends(login.login_manager)):
    return templates.TemplateResponse("logs_admin.html", {"request": request})