# Section to import standart module
from time import time
from datetime import datetime

# Section to import external module
import uvicorn
from fastapi import FastAPI
from fastapi import Request
from fastapi import WebSocket
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocketDisconnect

# Section to import morelia module
from mod import config

# Раскомментировать строчку ниже
# для перехода на работу с SQLite без ОРМ SQLObject
# import database.main as db

# Раскомментировать строчки ниже
# для перехода на работу с SQLite через ОРМ SQLObject
from mod import controller as db
import sqlobject as orm


# Connect to database
connection = orm.connectionForURI(config.LOCAL_SQLITE)
orm.sqlhub.processConnection = connection

server_started = datetime.now()

app = FastAPI()

templates = Jinja2Templates(directory='templates')

# Save clients session
# TODO:   При отключении нужно реализовать их удаление  подумать как их хранить
clients = []


@app.get('/')
def home_page(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@app.get('/status')
def status_page(request: Request):
    stats = {
        'Server time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Server uptime': str(datetime.now()-server_started),
        'Users': len(clients),
        'Messages': len(db.get_messages())
    }
    return templates.TemplateResponse('status.html',
                                      {'request': request,
                                       'stats': stats})


# Send all message from DB
async def get_all_messages(newclient):
    for message in db.get_messages():
        await newclient.send_json(message)


# Посылаем сообщение всем клиентам
async def send_message(mes):
    for client in clients:
        await client.send_json(mes)


# TODO: надо релизовать регистрацию
async def reg_user(data: dict) -> str:
    """The function registers the user who is not in the database.

    Args:
        data (dict): [description]

    Returns:
        str: returns a string value: 'true' or 'newreg'
    """
    password = data['password']
    username = data['username']
    if (dbpassword := db.get_userdata(username)):
        if password == dbpassword:
            return 'true'
        else:
            return 'false'
    else:
        db.save_userdata(username, password)
        return 'newreg'


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    client = websocket
    await get_all_messages(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data["mode"] == "message":
                message = {
                        "mode": "message",
                        "username": data["username"],
                        "text": data["text"],
                        "timestamp": time()
                        }
                db.save_message(message)
                print(message)
                await send_message(message)
            elif data["mode"] == "reg":
                message = {
                        "mode": "reg",
                        "status": await reg_user(data)
                        }
                await client.send_json(message)

    except WebSocketDisconnect as e:
        clients.remove(websocket)
        print(e)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
