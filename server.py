# ************** Standart module *********************
from datetime import datetime
from json import JSONDecodeError
# ************** Standart module end *****************


# ************** External module *********************
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
add_logging(debug_status=config.DEBUG_LEVEL)
# ************** Logging end **************************

# Record server start time
server_started = datetime.now()

# Connect to database
connection = orm.connectionForURI(config.LOCAL_SQLITE)
orm.sqlhub.processConnection = connection

# Server instance creation
app = FastAPI()

# Specifying where to load HTML page templates
templates = Jinja2Templates(directory=config.TEMPLATE_FOLDER)


# Save clients session
# TODO: Нужно подумать как их компактно хранить
clients = []


# Server home page
@app.get('/')
def home_page(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


# Server page with working statistics
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


# Chat websocket
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
            break
        except (RuntimeError, JSONDecodeError) as error:
            logger.info("".join(("Runtime or Decode error: ", str(error))))
            clients.remove(websocket)
            break
        else:
            if websocket.client_state.value == 0:
                await websocket.close(code=1000)
                clients.remove(websocket)


if __name__ == "__main__":
    print("to start the server, write the following command in the console:")
    print("uvicorn server:app --host 0.0.0.0 --port 8000 --reload --use-colors --http h11 --ws websockets &")
