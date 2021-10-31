from uuid import uuid4
from fastapi import APIRouter
from fastapi import Form
from starlette.requests import Request
from starlette.responses import HTMLResponse

from mod import models

router = APIRouter()


@router.post("/manage/delete_user")
def delete_user(request: Request, uuid: str = Form(...)):
    dbquery = models.UserConfig.selectBy(uuid=uuid).getOne()

    fake_uuid = str(uuid4().int)

    dbquery.login = "User deleted"
    dbquery.password = fake_uuid
    dbquery.hashPassword = fake_uuid
    dbquery.username = "User deleted"
    dbquery.authId = fake_uuid
    dbquery.email = ""
    dbquery.avatar = b""
    dbquery.bio = "deleted"
    dbquery.salt = b"deleted"
    dbquery.key = b"deleted"

    response = HTMLResponse("""
        <script>
            window.document.location.href = "./"
        </script>
    """)
    return response
