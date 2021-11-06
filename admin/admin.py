"""
    Copyright (c) 2020 - present NekrodNIK, Stepan Skriabin, rus-ai and other.
    Look at the file AUTHORS.md(located at the root of the project) to get the
    full list.

    This file is part of Morelia Server.

    Morelia Server is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Morelia Server is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with Morelia Server. If not, see <https://www.gnu.org/licenses/>.
"""

from fastapi import Depends
from fastapi.applications import FastAPI
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from pathlib import Path
from loguru import logger
import sqlobject as orm

from starlette.responses import RedirectResponse

from mod.db import models
from . import login, logs
from . import control as manage

app = FastAPI()

templates = Jinja2Templates(Path(__file__).parent / "templates")

app.include_router(login.router)
app.include_router(logs.router)
app.include_router(manage.router)

try:
    db_connection = orm.connectionForURI(login.database.get("uri"))
except Exception as ERROR:
    logger.exception(str(ERROR))
finally:
    orm.sqlhub.processConnection = db_connection


@app.exception_handler(login.NotAuthenticatedException)
def not_login_exception_handler(
        request: Request,
        exc: login.NotAuthenticatedException
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


# TODO Полностью доделать(на данный момент управление сервером не работает)
# после того, как будут сделаны методы работы с бд
@app.get("/manage")
def manage_admin(request: Request, user=Depends(login.login_manager)):
    return templates.TemplateResponse("manage_admin.html", {
        "request": request,
        "users": models.UserConfig.select()
    })


@app.get("/logs")
def manage_logs(request: Request, user=Depends(login.login_manager)):
    return templates.TemplateResponse("logs_admin.html", {"request": request})
