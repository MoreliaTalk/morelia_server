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

from datetime import datetime
from json import JSONDecodeError
import logging as standart_logging

from loguru import logger
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.routing import Route
from starlette.routing import WebSocketRoute
from starlette.websockets import WebSocket
from starlette.websockets import WebSocketDisconnect

from mod.config.instance import config_option
from mod.controller import MainHandler
from mod.db.dbhandler import DBHandler
from mod.log_handler import add_logging

db_connect: DBHandler | None = None


def on_startup():
    """
    This function run on start up server and init server initializes it.
    """

    global db_connect

    if config_option.logging.uvicorn_logging_disable:
        standart_logging.disable()

    # loguru logger on
    add_logging(config_option.logging.level)

    # Record server start time (UTC)
    server_started = datetime.now()

    # Set database connection
    db_connect = DBHandler(uri=config_option.database.url)
    db_connect.create_table()

    logger.info("Start server")
    logger.info(f"Started time {server_started}")


async def homepage(request: Request):
    """
    Rendered home page where presents information about current working server.

    Args:
        request(Request): not used

    Returns:
        (text/html): rendered text to html

    """

    return HTMLResponse("<h1>MoreliaServer</h1>")


# Chat websocket
async def websocket_endpoint(websocket: WebSocket):
    """
    Responsible for establishing a websocket connection.

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
    if websocket.client is not None:
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
            request = MainHandler(request=data,
                                  database=db_connect,
                                  protocol='mtp')
            response = await websocket.send_bytes(request.get_response())
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


# Server instance creation
app = Starlette(on_startup=[on_startup],
                routes=[Route("/",
                              endpoint=homepage),
                        WebSocketRoute("/ws",
                                       endpoint=websocket_endpoint)])


if __name__ == "__main__":
    print("to start the server, write the following command in the console:")
    print("uvicorn server:app --host 0.0.0.0 --port 8000 --reload --use-colors \
          --http h11 --ws websockets &")
