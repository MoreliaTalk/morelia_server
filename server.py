# ************** Standart module *********************
from datetime import datetime
from json import JSONDecodeError
import configparser
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
from mod import controller
from mod import models
# ************** Morelia module end ******************


# ************** Logging beginning *******************
from loguru import logger
from mod.logging import add_logging
# ************** Unicorn logger off ******************
import logging
logging.disable()
# ************** Logging end *************************

# ************** Read "config.ini" ********************
config = configparser.ConfigParser()
config.read('config.ini')
logging = config['LOGGING']
database = config["DATABASE"]
directory = config["TEMPLATES"]
# ************** END **********************************

# loguru logger on
add_logging(logging.getint("level"))

# Record server start time (UTC)
server_started = datetime.now()

# Connect to database
try:
    connection = orm.connectionForURI(database.get("uri"))
except Exception as ERROR:
    logger.exception(str(ERROR))
finally:
    orm.sqlhub.processConnection = connection

# Server instance creation
app = FastAPI()
logger.info("Start server")

# Specifying where to load HTML page templates
templates = Jinja2Templates(directory.get("folder"))


# Save clients session
# TODO: Нужно подумать как их компактно хранить
CLIENTS = []


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
        'Users': len(CLIENTS),
        'Messages': dbquery.count()
        }
    return templates.TemplateResponse('status.html',
                                      {'request': request,
                                       'stats': stats})


# Chat websocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Waiting for the client to connect via websockets
    await websocket.accept()
    CLIENTS.append(websocket)
    logger.info("".join(("Clients information: ",
                         "host: ", str(websocket.client.host),
                         " port: ", str(websocket.client.port))))
    logger.debug(f"Websocket scope: {str(websocket.scope)}")
    while True:
        try:
            # Receive a request from the client as a JSON object
            data = await websocket.receive_json()
            logger.success("Receive a request from client")
            logger.debug(f"Request: {str(data)}")
            # create a "client" object and pass the request body to
            # it as a parameter. The "get_response" method generates
            # a response in JSON-object format.
            client = controller.ProtocolMethods(data)
            response = await websocket.send_bytes(client.get_response())
            logger.info("Response sent to client")
            logger.debug(f"Result of processing: {response}")
        # After disconnecting the client (by the decision of the client,
        # the error) must interrupt the cycle otherwise the next clients
        # will not be able to connect.
        except WebSocketDisconnect as STATUS:
            logger.debug(f"Disconnection status: {str(STATUS)}")
            CLIENTS.remove(websocket)
            break
        except (RuntimeError, JSONDecodeError) as ERROR:
            CODE = 1002
            logger.exception(f"Runtime or Decode error: {str(ERROR)}")
            await websocket.close(CODE)
            logger.info(f"Close with code: {CODE}")
            CLIENTS.remove(websocket)
            break
        else:
            if websocket.client_state.value == 0:
                CODE = 1000
                # "code=1000" - normal session termination
                await websocket.close(CODE)
                CLIENTS.remove(websocket)
                logger.info(f"Close with code: {CODE}")


if __name__ == "__main__":
    print("to start the server, write the following command in the console:")
    print("uvicorn server:app --host 0.0.0.0 --port 8000 --reload --use-colors \
          --http h11 --ws websockets &")
