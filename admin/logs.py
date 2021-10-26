from fastapi import APIRouter
from fastapi import Depends
from starlette.requests import Request
from . import login

router = APIRouter()

log_list = str()


@router.get("/logs/get")
def get_logs(request: Request, user=Depends(login.login_manager)):
    return {"logs": log_list}


def loguru_handler(log):
    global log_list
    log_list += log
