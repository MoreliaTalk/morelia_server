from datetime import datetime
from json import JSONDecodeError

from loguru import logger
from starlette.applications import Starlette
from starlette.websockets import WebSocket
from starlette.websockets import WebSocketDisconnect
from mod.config.handler import read_config
from mod.config.models import ConfigModel
from mod.db.dbhandler import DBHandler
from mod.log_handler import add_logging
from mod.protocol.worker import MTProtocol


class MoreliaServer:
    _starlette_app: Starlette
    _config_options: ConfigModel
    _database: DBHandler

    def __init__(self):
        self._config_options = read_config()

        add_logging(self._config_options)

        self._database = DBHandler(uri=self._config_options.database.url)
        self._database.create_table()

        self._starlette_app = Starlette()

        self._starlette_app.add_websocket_route("/ws", self._ws_endpoint)

    def get_starlette_app(self):
        return self._starlette_app

    def _on_start(self):
        logger.info("Server started")
        logger.info(f"Started time {datetime.now()}")

    async def _ws_endpoint(self, websocket: WebSocket):
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
                                     database=self._database,
                                     config_option=self._config_options)
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
                    CODE = 1000  # normal session termination
                    await websocket.close(CODE)
                    logger.info(f"Close with code: {CODE}")


if __name__ != "__main__":
    _server = MoreliaServer()
    app = _server.get_starlette_app()
else:
    print("to start the server, write the following command in the console:")
    print("uvicorn server:app --host 0.0.0.0 --port 8000 --reload "
          "--use-colors --http h11 --ws websockets &")
