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
from starlette.responses import RedirectResponse

from mod.db.dbhandler import DBHandler
from config import DATABASE
from . import login
from . import logs
from . import control as manage

app = FastAPI()

templates = Jinja2Templates(Path(__file__).parent / "templates")

app.include_router(login.router)
app.include_router(logs.router)
app.include_router(manage.router)

db_connect = DBHandler(DATABASE.get('URI'))


@app.exception_handler(login.NotAuthenticatedException)
def not_login_exception_handler(request: Request,
                                exc: login.NotAuthenticatedException):
    """
    Catches exception login.NotAuthenticatedException and redirects the user to the login page("/admin/login/")

    Args:
        request(Request): request to the server
        exc(login.NotAuthenticatedException): catchable user authentication error

    Returns:
        (RedirectResponse): redirect response to /admin/login
    """
    return RedirectResponse(url="/admin/login")


@app.get("/login")
def login_admin(request: Request):
    """
    The function is triggered when a request is received for the /login address
    and returns a response generated from login.html

    Args:
        request(Request): request to the server

    Returns:
        (templates.TemplateResponse): response generated from login.html template

    """
    return templates.TemplateResponse("login.html", {
                                        "request": request
                                        })


@app.get("/")
def index_admin(request: Request,
                user=Depends(login.login_manager)):
    """
    Returns a response with the main page of the admin panel

    Args:
        request(Request): request to the server
        user: user authentication check

    Returns:
        (templates.TemplateResponse): response generated from index_admin.html template
    """
    return templates.TemplateResponse("index_admin.html", {
                                        "request": request
                                        })


@app.get("/status")
def status_admin(request: Request,
                 user=Depends(login.login_manager)):
    """
        Returns a response with the status page of the admin panel

        Args:
            request(Request): request to the server
            user: user authentication check

        Returns:
            (templates.TemplateResponse): response generated from status_admin.html template
        """
    dbquery = db_connect.get_table_count()
    return templates.TemplateResponse("status_admin.html",
                                      {"request": request,
                                       "Messages_count": dbquery.message_count,
                                       "Flows_count": dbquery.flow_count,
                                       "Users_count": dbquery.user_count
                                       })


# TODO Полностью доделать(на данный момент управление сервером не работает)
# после того, как будут сделаны методы работы с бд
@app.get("/manage")
def manage_admin(request: Request,
                 user=Depends(login.login_manager)):
    """
        Returns a response with the mange page of the admin panel

        Args:
            request(Request): request to the server
            user: user authentication check

        Returns:
            (templates.TemplateResponse): response generated from manage_admin.html template
    """
    dbquery = db_connect.get_all_user()
    return templates.TemplateResponse("manage_admin.html", {
                                        "request": request,
                                        "users": dbquery.count()
                                        })


@app.get("/logs")
def manage_logs(request: Request,
                user=Depends(login.login_manager)):
    """
        Returns a response with the logs view page of the admin panel

        Args:
            request(Request): request to the server
            user: user authentication check

        Returns:
            (templates.TemplateResponse): response generated from logs_admin.html template
    """
    return templates.TemplateResponse("logs_admin.html", {
                                        "request": request
                                        })
