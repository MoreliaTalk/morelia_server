# ************** Standart module *********************
import json
from time import time
from datetime import datetime
# ************** Standart module end *****************


# ************** External module *********************
import uvicorn
from fastapi import FastAPI
from fastapi import Request
from fastapi import WebSocket
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocketDisconnect
# ************** External module end *****************


# ************** Morelia module **********************
from mod import config

# Comment on the line below to start working
# with SQLite without SQLObject ORM
# import database.main as db

# Comment on the lines below to switch to
# working with SQLite via SQLObject ORM
from mod import controller as db
import sqlobject as orm
# ************** Morelia module end ********************


# ************** Logging beginning *********************
from loguru import logger
from settings.logging import add_logging

# ### unicorn logger off
# import logging
# logging.disable()

# ### loguru logger on
add_logging(debug_status=uvicorn.config.logger.level)
# ************** Logging end **************************


# Connect to database
connection = orm.connectionForURI(config.LOCAL_SQLITE)
orm.sqlhub.processConnection = connection

server_started = datetime.now()

app = FastAPI()

templates = Jinja2Templates(directory=config.TEMPLATE_FOLDER)


# Save clients session
# TODO: При отключении нужно реализовать их удаление подумать как их хранить
clients = []


# Server home page
@app.get('/')
def home_page(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


# Page of server with statistics of it's work
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
async def get_all_messages(newclient) -> None:
    for message in db.get_messages():
        await newclient.send_json(message)


# Sending a message to all clients
async def send_message(message) -> None:
    for client in clients:
        await client.send_json(message)


# TODO: надо релизовать регистрацию
async def reg_user(data: dict) -> str:
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
            if data.get("mode") == "message":
                message = {
                        "mode": "message",
                        "username": data["username"],
                        "text": data["text"],
                        "timestamp": time()
                        }
                db.save_message(message)
                logger.debug(f'{message}')
                await send_message(message)
            elif data.get("mode") == "reg":
                message = {
                        "mode": "reg",
                        "status": await reg_user(data)
                        }
                await client.send_json(message)
            else:
                message = db.serve_request(json.dumps(data))
                if message != {}:
                    logger.debug(f'{message}')
                    await send_message(message)

    except WebSocketDisconnect as error:
        logger.info('Disconnected ' + websocket.client.host)
        clients.remove(websocket)
        logger.info(error)


if __name__ == "__main__":
    uvicorn.run(app, host=config.UVICORN_HOST,
                port=config.UVICORN_PORT,
                use_colors=False)
