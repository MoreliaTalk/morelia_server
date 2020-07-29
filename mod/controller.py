import random
from time import time

from mod import models
from mod import config
from mod import api


def save_userdata(username: str, password: str) -> None:
    """The function saves the user name and password to the database.
    There is no check for the data type.

    Args:
        username (str): required
        password (str): required

    Returns:
        None
    """
    userID = random.getrandbits(64)
    models.User(UUID=userID, password=password, login=username, username=username)
    return


def get_userdata(username: str):
    """The function checks the presence of the user in the database.

    Args:
        username (str): required

    Returns:
        bool: True or False
    """
    dbdata = models.User.select(models.User.q.username == username)
    if dbdata.count() != 0:
        return dbdata[0].password
    else:
        return None


def save_message(message: dict) -> None:
    """The function stores the message in the database.

    Args:
        message (dict): [description]

    Returns:
        None
    """
    user = models.User.select(models.User.q.username == message['username'])
    models.Message(text=message['text'],
                   userID=user[0].UUID,
                   flowID=0,
                   time=message['timestamp'])
    return


def get_messages() -> list:
    """The function receives all the messages
    from the database and converts them into a list.

    Args:
        No args.

    Returns:
        list: The list contains the following dictionary:
        {
            'mode': 'message',
            'username': str,
            'text': str,
            'time': int
        }
    """
    dbquery = models.Message.select(models.Message.q.id > 0)
    messages = []
    for data in dbquery:
        user = models.User.select(models.User.q.UUID == data.userID)
        messages.append({
            "mode": "message",
            "username": user[0].username,
            "text": data.text,
            "timestamp": data.time
        })
    return messages


def register_user(username: str, password: str) -> str:
    """The function registers the user who is not in the database.

    Args:
        username (str): required
        password (str): required

    Returns:
        str: returns a string value: 'true' or 'newreg'
    """
    if dbpassword := get_userdata(username):
        if password == dbpassword:
            return 'true'
        else:
            return 'false'
    else:
        save_userdata(username, password)
        return 'newreg'


def serve_request(request_json) -> dict:
    """The function try serve user request and return result status.

    Args:
        No args.

    Returns:
        Response for sending to user  - successfully served
        (error response - if any kind of problems)
    """
    try:
        request = api.ValidJSON.parse_raw(request_json)
    except api.ValidationError as error:
        message = {
            'type': 'error',
            'errors': {
                'time': time(),
                'status': 'Bad Request',
                'code': 400,
                'detail': 'JSON validation error'
            },
            'jsonapi': {
                'version': config.API_VERSION
            },
            'meta': None
        }
        return message
    if request.type == 'register_user':
        message = {
            "mode": "reg",
            "status": register_user(request.data.user.login, request.data.user.password)
        }
        return message
    else:
        message = {
            'type': request.type,
            'errors': {
                'time': time(),
                'status': 'Bad Request',
                'code': 400,
                'detail': 'Method not supported by server'
            },
            'jsonapi': {
                'version': config.API_VERSION
            },
            'meta': None
        }
        return message


def get_update():
    pass


def send_message():
    pass


def all_message():
    pass


def all_flow():
    pass


def user_info():
    pass


def authentication():
    pass


def delete_user():
    pass


def delete_message():
    pass


def edited_message():
    pass


def ping_pong():
    pass