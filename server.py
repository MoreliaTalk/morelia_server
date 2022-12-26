"""
Copyright (c) 2020 - present MoreliaTalk team and other.
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
from starlette.websockets import WebSocket
from starlette.websockets import WebSocketDisconnect

from mod.config.handler import ConfigHandler
from mod.db.dbhandler import DBHandler
from mod.log_handler import add_logging
from mod.protocol.worker import MTProtocol

db_connect: DBHandler | None = None


class MoreliaServer:
    def __init__(self):
        config_handler = ConfigHandler()
        self.config_option = config_handler.read()

        self.db_connect = DBHandler(uri=self.config_option.database.url)
        self.db_connect.create_table()

        # TODO: move to loger module
        if self.config_option.logging.uvicorn_logging_disable:
            standart_logging.disable()

        add_logging(self.config_option)

        self.starlette_app = Starlette()

        self.starlette_app.add_event_handler(event_type="startup", func=self._on_server_started)
        self.starlette_app.add_route(path="/", route=self._homepage)
        self.starlette_app.add_websocket_route(path="/ws", route=self._websocket_endpoint)

    def get_starlette_app(self) -> Starlette:
        return self.starlette_app

    async def _on_server_started(self):
        logger.info("Start server")

        server_started = datetime.now()
        logger.info(f"Started time {server_started}")

    async def _homepage(self, request: Request):
        """
        Rendered home page where presents information about current working server.

        Args:
            request(Request): not used

        Returns:
            (text/html): rendered text to html

        """

        return HTMLResponse("<h1>MoreliaServer</h1>")

    async def _websocket_endpoint(self, websocket: WebSocket) -> None:
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
                request = MTProtocol(request=data,
                                     database=self.db_connect,
                                     config_option=self.config_option)
                await websocket.send_text(request.get_response())
                logger.info("Response sent to client")
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
    print("uvicorn server:app --host 0.0.0.0 --port 8000 --reload \
           --use-colors --http h11 --ws websockets &")
