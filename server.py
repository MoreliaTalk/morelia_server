"""
    Copyright (c) 2020 - present NekrodNIK, Stepan Skriabin, rus-ai and other.
    Look at the file AUTHORS.md(located at the root of the project) to get the
    full list.

    This file is part of Morelia Server.

    Morelia Server is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Morelia Server is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with Morelia Server. If not, see <https://www.gnu.org/licenses/>.
"""

# ************** Standart module *********************
import os
from datetime import datetime
from json import JSONDecodeError
# ************** Standart module end *****************


# ************** External module *********************
from fastapi import FastAPI
from fastapi import Request
from fastapi import WebSocket
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocketDisconnect
# ************** External module end *****************


# ************** Morelia module **********************
from mod.controller import MainHandler
from mod.db.dbhandler import DBHandler
from admin import admin
from mod.config.config import ConfigHandler
# ************** Morelia module end ******************


# ************** Logging beginning *******************
from loguru import logger
from mod.logging import add_logging
import logging as standart_logging
# ************** Unicorn logger off ******************
# Get parameters contains in config.ini
config = ConfigHandler()
config_option = config.read()
if config_option.uvicorn_logging_disable:
    standart_logging.disable()
# ************** Logging end *************************

# loguru logger on
add_logging(config_option.level)

# Record server start time (UTC)
server_started = datetime.now()

# Server instance creation
app = FastAPI()
logger.info("Start server")

# Specifying where to load HTML page templates
templates = Jinja2Templates(config_option.folder)

# Search and filtered static files path
main_path = os.getcwd()
base_path = os.path.split(main_path)
if base_path[1] == 'tests':
    file_static = os.path.join(base_path[0], 'static')
else:
    file_static = os.path.join(main_path, 'static')

# Set database connection
db_connect = DBHandler(uri=config_option.uri)
db_connect.create_table()


app.mount("/admin",
          admin.app)

app.mount("/static",
          StaticFiles(directory=file_static),
          name="static")


@app.get('/')
def home_page(request: Request):
    """
    Rendered home page where presents information about current working server

    Args:
        request(Request): not used

    Returns:
        (text/html): rendered text to html

    """

    return HTMLResponse("<h1>MoreliaTalkServer</h1>")


# Chat websocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Responsible for establishing a websocket connection between server and
    client and exchanging requests/responses.

    Notes:
        Waiting for client to connect via websockets, after which receive a
        request from client as a JSON-object create request object and pass
        to class MainHandler.

        After MTProtocol or MatrixProtocol processing request, "get_response"
        method generates response in JSON-object format.

        After disconnecting the client (by decision of client or error)
        must interrupt cycle otherwise the next clients will not be able
        to connect.

        `code = 1000` - normal session termination

    Args:
        websocket(WebSocket):

    Returns:
        websocket(WebSocket):
    """

    # Waiting for the client to connect via websockets
    await websocket.accept()
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
            client_request = MainHandler(request=data,
                                         database=db_connect,
                                         protocol='mtp')
            response = await websocket.send_bytes(client_request.get_response())
            logger.info("Response sent to client")
            logger.debug(f"Result of processing: {response}")
        # After disconnecting the client (by the decision of the client,
        # the error) must interrupt the cycle otherwise the next clients
        # will not be able to connect.
        except WebSocketDisconnect as STATUS:
            logger.debug(f"Disconnection status: {str(STATUS)}")
            break
        except (RuntimeError, JSONDecodeError) as ERROR:
            CODE = 1002
            logger.exception(f"Runtime or Decode error: {str(ERROR)}")
            await websocket.close(CODE)
            logger.info(f"Close with code: {CODE}")
            break
        else:
            if websocket.client_state.value == 0:
                CODE = 1000
                # "code=1000" - normal session termination
                await websocket.close(CODE)
                logger.info(f"Close with code: {CODE}")


if __name__ == "__main__":
    print("to start the server, write the following command in the console:")
    print("uvicorn server:app --host 0.0.0.0 --port 8000 --reload --use-colors \
          --http h11 --ws websockets &")
