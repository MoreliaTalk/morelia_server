# ************** Standart module *********************
from datetime import datetime
# ************** Standart module end *****************


# ************** External module *********************
import uvicorn
from fastapi import FastAPI
from fastapi import Request
from fastapi import WebSocket
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocketDisconnect
import sqlobject as orm
# ************** External module end *****************


# ************** Morelia module **********************
from mod import config
from mod import controller
from mod import models
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


# Static page
# Server home page
@app.get('/')
def home_page(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


# Page of server with statistics of it's work
@app.get('/status')
def status_page(request: Request):
    dbquery = models.Message.select(models.Message.q.time >= 1)
    stats = {
        'Server time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Server uptime': str(datetime.now()-server_started),
        'Users': len(clients),
        'Messages': dbquery.count()
        }
    return templates.TemplateResponse('status.html',
                                      {'request': request,
                                       'stats': stats})


# Websocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    logger.info("".join(("Clients information: ",
                         "host: ", str(websocket.client.host),
                         " port: ", str(websocket.client.port))))
    logger.debug(str(websocket.scope))
    while True:
        try:
            data = await websocket.receive_json()
            logger.debug(str(data))
            client = controller.ProtocolMethods(data)
            await websocket.send_json(client.get_response(), mode='binary')
        except WebSocketDisconnect as error:
            logger.info("".join(("Disconnection error: ", str(error))))
            clients.remove(websocket)
            logger.info(error)
        else:
            if websocket.client_state.value == 0:
                await websocket.close(code=1000)
                clients.remove(websocket)


if __name__ == "__main__":
    uvicorn.run(app, host=config.UVICORN_HOST,
                port=config.UVICORN_PORT,
                debug=True,
                log_level="trace",
                http="h11",
                ws="websockets",
                use_colors=True)
