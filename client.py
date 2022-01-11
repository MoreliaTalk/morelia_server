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
LOCALHOST = 'ws://localhost:8000/ws'

# Registration information from superuser
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
    "type": "authentication",
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
            "uuid": None,
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
def send_message(message: Union[dict, str] = AUTH, 
                 uri: str = LOCALHOST) -> bytes:
    """Sending a message via websockets, with a response

    Args:
        message ([dict], required): message.
        uri ([str], required): server address like 'ws://host:port/ws'

    Returns:
        message [bytes]: Response as a byte object.
    """
    result = b'None'
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
