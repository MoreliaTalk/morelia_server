from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()

templates = Jinja2Templates(Path(__file__).parent / "templates")

@router.get("/admin")
def index_admin(request: Request):
    return templates.TemplateResponse("index_admin.html", {"request": request})
