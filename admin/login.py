from pathlib import Path
from loguru import logger

from fastapi import APIRouter, Depends, Request
from fastapi_login import LoginManager
from fastapi.security import OAuth2PasswordRequestForm

from configparser import ConfigParser

from starlette.responses import HTMLResponse
from mod import models
import sqlobject as orm

config = ConfigParser()
config.read(Path(__file__).parent.parent / "config.ini")

SECRET_KEY = config["ADMIN"].get("SECRET_KEY")

database = config["DATABASE"]

try:
    db_connection = orm.connectionForURI(database.get("uri"))
except Exception as ERROR:
    logger.exception(str(ERROR))
finally:
    orm.sqlhub.processConnection = db_connection

router = APIRouter()


class NotLoginException(Exception):
    pass


login_manager = LoginManager(
    SECRET_KEY,
    token_url="/login/token",
    use_cookie=True,
    use_header=False
)

login_manager.not_authenticated_exception = NotLoginException


@login_manager.user_loader()
def get_admin_user_data(username: str):
    data = models.Admin.selectBy(username=username)
    if data.count():
        return data[0]


@router.post("/login/token")
def login_token(data: OAuth2PasswordRequestForm = Depends()):
    admin_user_data_db = get_admin_user_data(data.username)
    if not admin_user_data_db:
        return HTMLResponse(
            """
            <script>
            window.document.location.href = "./"
            </script>
            """
        )
    elif data.password != admin_user_data_db.password:
        return HTMLResponse(
            """
            <script>
            window.document.location.href = "./"
            </script>
            """
        )

    token = login_manager.create_access_token(
        data={
            "sub": data.username
        }
    )

    response = HTMLResponse(
        """
        <script>
        window.document.location.href = "../"
        </script>
        """
    )
    login_manager.set_cookie(response, token)

    return response


@router.post("/login/logout")
def logout(request: Request):
    incorrect_token = "MoreliaTalk"

    response = HTMLResponse(
        """
        <script>
        window.document.location.href = "../"
        </script>
        """
    )

    login_manager.set_cookie(response, incorrect_token)

    return response
