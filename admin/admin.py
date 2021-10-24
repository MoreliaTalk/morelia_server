from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from pathlib import Path
from . import login

router = APIRouter()

templates = Jinja2Templates(Path(__file__).parent / "templates")

router.include_router(login.router)


@router.get("/admin")
def index_admin(request: Request, user=Depends(login.login_manager)):
    return templates.TemplateResponse("index_admin.html", {"request": request})
