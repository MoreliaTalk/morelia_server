# ************** Standart module *********************
import json
from typing import Union
# ************** Standart module end *****************


# ************** External module *********************
import websocket
# ************** External module end *****************


# ************** Logging beginning *******************
from loguru import logger
from mod.logging import add_logging
# ************** Logging end *************************


# logger on INFO
add_logging(20)

# URL and Port
URI = 'ws://localhost:8000/ws'

# Registration infirmation from superuser
user_login = 'login'
user_password = 'password'
salt = b'salt'
key = b'key'
uuid = '123456789'

GET_UPDATE = {
    "type": "get_update",
    "data": {
        "time": 111,
        "user": [{
            "uuid": uuid,
            "auth_id": "auth_id",
            }],
        "meta": None
        },
    "jsonapi": {
        "version": "1.0"
        },
    "meta": None
    }

AUTH = {
    "type": "auth",
    "data": {
        "user": [{
            "password": user_password,
            "login": user_login
            }],
        "meta": None
        },
    "jsonapi": {
        "version": "1.0"
        },
    "meta": None
    }

ADD_FLOW = {
    "type": "add_flow",
    "data": {
        "flow": [{
            "type": "group",
            "title": "title",
            "info": "info",
            "owner": uuid,
            "users": [uuid]
            }],
        "user": [{
            "uuid": uuid,
            "auth_id": "auth_id",
            }],
        "meta": None
        },
    "jsonapi": {
        "version": "1.0"
        },
    "meta": None
    }

ALL_FLOW = {
    "type": "all_flow",
    "data": {
        "user": [{
            "uuid": uuid,
            "auth_id": "auth_id"
            }],
        "meta": None
        },
    "jsonapi": {
        "version": "1.0"
        },
    "meta": None
    }


# Chat websocket
def send_message(message: Union[dict, str] = AUTH, uri: str = URI) -> bytes:
    result = b'None'
    """Sending a message via websockets, with a response

    Args:
        message ([dict], required): message.
        uri ([str], required): server address like 'ws://host:port/ws'

    Returns:
        message [bytes]: Response as a byte object.
    """
    ws = websocket.WebSocket()
    try:
        ws.connect(uri)
        logger.success("Setting up connection")
    except Exception as error:
        logger.exception(str(error))
        logger.error("Problems in connection to server")
    else:
        logger.info(f"Connection status: {ws.getstatus()}")
        ws.send(json.dumps(message))
        logger.info("Message send")
        result = ws.recv()
        logger.info("Server response received")
        ws.close(status=1000)
        logger.success("Session with server ended successfully")
    finally:
        ws.close(status=1002)
    return result


if __name__ == "__main__":
    result = send_message()
    logger.debug(f"Server response: {json.loads(result)}")
    logger.info("END")
