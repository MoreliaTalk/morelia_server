from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi_login import LoginManager
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException

from configparser import ConfigParser
from mod import models
import sqlobject as orm

config = ConfigParser()
config.read(Path(__file__).parent.parent / "config.ini")

SECRET_KEY = config["ADMIN"].get("SECRET_KEY")

database = config["DATABASE"]
db_connection = orm.connectionForURI(database.get("uri"))
orm.sqlhub.processConnection = db_connection

router = APIRouter()

login_manager = LoginManager(SECRET_KEY, token_url="/admin/login/token")


@login_manager.user_loader()
def get_admin_user_data(username: str):
    return models.Admin.selectBy(username=username)[0]


@router.post("/admin/login/token")
def login_token(data: OAuth2PasswordRequestForm = Depends()):
    admin_user_data_db = get_admin_user_data(data.username)
    if not admin_user_data_db:
        raise InvalidCredentialsException
    elif data.password != admin_user_data_db.password:
        raise InvalidCredentialsException

    token = login_manager.create_access_token(
        data={
            "sub": data.username
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }
