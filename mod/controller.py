import random
from time import time
from pydantic import ValidationError

from mod import models
from mod import config
from mod import api
from mod import lib


def user_info_for_server(uuid: int = None,
                         login: str = None) -> dict:
    """Provides information about all personal settings of user
    (in a server-friendly form)

    Args:
        uuid (int, optional): Unique User ID
        login (str, optional): user login

    Returns:
        dict
    """
    if uuid:
        dbquery = models.User.select(models.User.q.uuid == uuid)
    elif login:
        dbquery = models.User.select(models.User.q.login == login)
    else:
        return None

    if dbquery.count():
        data_user = {
                'uuid': dbquery[0].uuid,
                'login': dbquery[0].login,
                'password': dbquery[0].password,
                'username': dbquery[0].username,
                'is_bot': dbquery[0].isBot,
                'auth_id': dbquery[0].authId,
                'email': dbquery[0].email,
                'avatar': dbquery[0].avatar,
                'bio': dbquery[0].bio
            }
        return data_user
    else:
        return None


def check_uuid_and_auth_id(uuid: int, auth_id: str) -> bool:
    """Function checks the correctness of uuid and auth_id

    Args:
        uuid (int, requires): Unique User ID
        auth_id (str, requires): authentification ID

    Returns:
        bool
    """
    dbquery = models.User.select(models.User.q.uuid == uuid)
    if dbquery.count():
        if auth_id == dbquery[0].authId:
            return True
        else:
            return False
    else:
        return False


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
    models.User(uuid=userID,
                password=password,
                login=username,
                username=username)
    return


def save_message(message: dict) -> None:
    """The function stores the message in the database.

    Args:
        message (dict): [description]

    Returns:
        None
    """
    user = models.User.select(models.User.q.username ==
                              message['username'])
    models.Message(text=message['text'],
                   userID=user[0].uuid,
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
        user = models.User.select(models.User.q.uuid ==
                                  data.userID)
        messages.append({
            "mode": "message",
            "username": user[0].username,
            "text": data.text,
            "timestamp": data.time
        })
    return messages


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
    except ValidationError as error:
        response = {
            "type": "errors",
            "data": None,
            "errors": None,
            "jsonapi": {
                "version": config.API_VERSION
            },
            "meta": None
        }
        response['errors'] = lib.error_catching(error)
        return response
    else:
        if request.type == 'ping-pong':
            return ping_pong(request)
        elif request.type == 'register_user':
            return register_user(request)
        elif request.type == 'send_message':
            return send_message(request)
        elif request.type == 'all_flow':
            return all_flow(request)
        elif request.type == 'add_flow':
            return add_flow(request)
        elif request.type == 'all_messages':
            return all_messages(request)
        elif request.type == 'user_info':
            return user_info(request)
        elif request.type == 'auth':
            return authentification(request)
        elif request.type == 'delete_user':
            return delete_user(request)
        elif request.type == 'delete_message':
            return delete_message(request)
        elif request.type == 'edited_message':
            return edited_message(request)
        elif request.type == "get_update":
            return get_update(request)
        else:
            return errors(request)


# Implementation of methods described in Morelia Protocol
def register_user(request: api.ValidJSON) -> dict:
    """The function registers the user who is not in the database.
    Note: This version also authentificate user, that exist in database
    Future version will return error if login exist in database

    Args:
        request (api.ValidJSON): client request - a set of data that was
        validated by "pydantic".

    Returns:
        dict: returns JSON reply to client
    """
    response = {
        "type": request.type,
        'data': None,
        'errors': None,
        'jsonapi': {
            'version': config.API_VERSION
            },
        'meta': None
        }
    if user_info_for_server(login=request.data.user.login) is None:
        # TODO
        # generate authID: store and return to user
        # generate salt, and create hash password
        userID = random.getrandbits(64)
        models.User(uuid=userID,
                    password=request.data.user.password,
                    login=request.data.user.login,
                    username=request.data.user.login)
        response['errors'] = lib.error_catching(201)
    else:
        # TODO поменять тип ошибки на 409
        response['errors'] = lib.error_catching(400)

    return response


def get_update(request: api.ValidJSON) -> dict:
    """The function displays messages of a specific flow,
    from the timestamp recorded in the request to the server timestamp,
    retrieves them from the database
    and issues them as an array consisting of JSON

    Args:
        request (api.ValidJSON): client request - a set of data that was
        validated by "pydantic".

    Returns:
        dict: [description]
    """
    get_time = time()
    response = {
        "type": request.type,
        "data": None,
        'errors': None,
        'jsonapi': {
            'version': config.API_VERSION
            },
        'meta': None
        }

    if check_uuid_and_auth_id(request.data.user.uuid,
                              request.data.user.auth_id) is False:
        response["errors"] = lib.error_catching(401)
        return response

    dbquery_flow = models.Flow.select(models.Flow.q.flowId ==
                                      request.data.flow.id)
    if dbquery_flow.count():
        data = {
            "time": get_time,
            "flow": {
                "id": dbquery_flow[0].flowId,
                "time": dbquery_flow[0].timeCreated,
                "type": dbquery_flow[0].flowType,
                "title": dbquery_flow[0].title,
                "info": dbquery_flow[0].info
                }
            }
        response['data'] = data
    else:
        response['errors'] = lib.error_catching(404, 'Flow Not Found')
        return response

    # TODO нужно реализовать фильтрацию по времени через SQLObject
    dbquery_message = models.Message.select(models.Message.q.flowID ==
                                            request.data.flow.id)
    if dbquery_message.count():
        messages = {}
        for i in dbquery_message:
            message = {
                i.id: {
                    "flowID": i.flowID,
                    "userID": i.userID,
                    "text": i.text,
                    "time": i.time,
                    "filePicture": i.filePicture,
                    "fileVideo": i.fileVideo,
                    "fileAudio": i.fileAudio,
                    "fileDocument": i.fileDocument,
                    "emoji": i.emoji,
                    "editedTime": i.editedTime,
                    "editedStatus": i.editedStatus
                    }
                }
            messages.update(message)
        data = {
            'user': {
                'uuid': request.data.user.uuid,
                'auth_id': request.data.user.auth_id
                },
            'messages': messages,
            'meta': None
            }
        response.update(data)
        response['errors'] = lib.error_catching(200)
    else:
        response["errors"] = lib.error_catching(404, "Message Not Found")
    return response


def send_message(request: api.ValidJSON) -> dict:
    """The function saves user message in the database.

    Args:
        request (api.ValidJSON): client request - a set of data that was
        validated by "pydantic"

    Returns:
        dict: returns JSON reply to client
    """
    get_time = time()
    response = {
        'type': request.type,
        'data': {
            'time': get_time,
            'meta': None
            },
        'errors': None,
        'jsonapi': {
            'version': config.API_VERSION
            },
        'meta': None
        }

    if check_uuid_and_auth_id(request.data.user.uuid,
                              request.data.user.auth_id) is False:
        response['errors'] = lib.error_catching(401)
        return response

    check_user_in_db = models.User.select(models.User.q.uuid ==
                                          request.data.user.uuid)
    check_flow_in_db = models.Flow.select(models.Flow.q.id ==
                                          request.data.flow.id)
    models.Message(text=request.data.message.text,
                   time=get_time,
                   user=check_user_in_db,
                   flow=check_flow_in_db)
    response['errors'] = lib.error_catching(200)
    return response


def add_flow(request: api.ValidJSON) -> dict:
    """Function allows you to add a new flow to the database

    Args:
        request (api.ValidJSON): client request - a set of data that was
        validated by "pydantic".

    Returns:
        dict: [description]
    """
    get_time = time()
    response = {
        'type': request.type,
        'data': None,
        'errors': None,
        'jsonapi': {
            'version': config.API_VERSION
            },
        'meta': None
        }

    if check_uuid_and_auth_id(request.data.user.uuid,
                              request.data.user.auth_id) is False:
        response['errors'] = lib.error_catching(401)
        return response

    flow_id = random.getrandbits(64)
    try:
        models.Flow(flowId=flow_id,
                    timeCreated=get_time,
                    flowType=request.data.flow.type,
                    title=request.data.flow.title,
                    info=request.data.flow.info)
    except Exception as error:
        response['errors'] = lib.error_catching(error)
    else:
        response['errors'] = lib.error_catching(200)
    return response


def all_flow(request: api.ValidJSON) -> dict:
    """Function allows to get a list of all flows and
    information about them from the database

    Args:
        request (api.ValidJSON): client request - a set of data that was
        validated by "pydantic".

    Returns:
        dict: [description]
    """
    get_time = time()
    response = {
        'type': request.type,
        'data': None,
        'errors': None,
        'jsonapi': {
            'version': config.API_VERSION
            },
        'meta': None
        }

    if check_uuid_and_auth_id(request.data.user.uuid,
                              request.data.user.auth_id) is False:
        response['errors'] = lib.error_catching(401)
        return response

    flows = {}
    dbquery = models.Flow.select(models.Flow.q.id > 0)
    for i in dbquery:
        flow = {
            i.id: {
                "flowId": i.flowId,
                "timeCreated": i.timeCreated,
                "flowType": i.flowType,
                "title": i.title,
                "info": i.info
                }
            }
        flows.update(flow)
    data = {
            'time': get_time,
            'flow': flows,
            'meta': None
            }
    response['data'] = data
    response['errors'] = lib.error_catching(200)
    return response


def user_info(request: api.ValidJSON) -> dict:
    """Provides information about all personal settings of user.

    Args:
        request (api.ValidJSON): client request - a set of data that was
        validated by "pydantic".

    Returns:
        dict: [description]
    """
    get_time = time()
    response = {
        "type": request.type,
        "data": None,
        'errors': None,
        'jsonapi': {
            'version': config.API_VERSION
            },
        'meta': None
        }

    if check_uuid_and_auth_id(request.data.user.uuid,
                              request.data.user.auth_id) is False:
        response['errors'] = lib.error_catching(401)
        return response

    dbquery = models.User.selectBy(uuid=request.data.user.uuid,
                                   authId=request.data.user.auth_id)
    data = {
        'time': get_time,
        'user': {
            'uuid': dbquery[0].uuid,
            'login': dbquery[0].login,
            'password': dbquery[0].password,
            'username': dbquery[0].username,
            'is_bot': dbquery[0].isBot,
            'auth_id': dbquery[0].authId,
            'email': dbquery[0].email,
            'avatar': dbquery[0].avatar,
            'bio': dbquery[0].bio
            },
        'meta': None
        }
    response["data"] = data
    response['errors'] = lib.error_catching(200)
    return response


def authentification(request: api.ValidJSON) -> dict:
    """Performs authentification of registered client,
    with issuance of a unique hash number of connection session.
    During authentification password transmitted by client
    and password contained in server database are verified.

    Args:
        request (api.ValidJSON): client request - a set of data that was
        validated by "pydantic".

    Returns:
        dict: [description]
    """
    get_time = time()
    response = {
        "type": request.type,
        "data": None,
        'errors': None,
        'jsonapi': {
            'version': config.API_VERSION
            },
        'meta': None
        }
    dbquery = models.User.selectBy(login=request.data.user.login,
                                   password=request.data.user.password)
    if dbquery.count():
        # TODO После внесения изменений в протокол
        # переделать алгоритм авторизации
        generator = lib.Hash(dbquery[0].password,
                             dbquery[0].salt,
                             uuid=dbquery[0].uuid)
        dbquery[0].authId = generator.auth_id()
        data = {
            'time': get_time,
            'user': {
                'uuid': dbquery[0].uuid,
                'auth_id': dbquery[0].authId
                },
            'meta': None
            }
        response["data"] = data
        response['errors'] = lib.error_catching(200)
    else:
        response["errors"] = lib.error_catching(404)
    return response


def delete_user(request: api.ValidJSON) -> dict:
    """Function irretrievably deletes the user from the database.

    Args:
        request (api.ValidJSON): client request - a set of data that was
        validated by "pydantic".

    Returns:
        dict: [description]
    """
    response = {
        "type": request.type,
        "data": None,
        'errors': None,
        'jsonapi': {
            'version': config.API_VERSION
            },
        'meta': None
        }

    if check_uuid_and_auth_id(request.data.user.uuid,
                              request.data.user.auth_id) is False:
        response['errors'] = lib.error_catching(401)
        return response

    dbquery = models.User.selectBy(login=request.data.user.login,
                                   password=request.data.user.password)
    if dbquery.count():
        data = {
            'user': {
                'uuid': dbquery[0].uuid,
                'login': dbquery[0].login
                },
            'meta': None
            }
        dbquery[0].delete(dbquery[0].id)
        response["data"] = data
        response['errors'] = lib.error_catching(200)
    else:
        response["errors"] = lib.error_catching(404)

    return response


def delete_message(request: api.ValidJSON) -> dict:
    """Function deletes the message from the database Message table by its ID.

    Args:
        request (api.ValidJSON): client request - a set of data that was
        validated by "pydantic".

    Returns:
        dict: [description]
    """
    response = {
        "type": request.type,
        "data": None,
        'errors': None,
        'jsonapi': {
            'version': config.API_VERSION
            },
        'meta': None
        }
    if check_uuid_and_auth_id(request.data.user.uuid,
                              request.data.user.auth_id) is False:
        response['errors'] = lib.error_catching(401)
        return response

    dbquery = models.Message.select(models.Message.q.id ==
                                    request.data.message.id)
    if dbquery.count():
        dbquery[0].delete(dbquery[0].id)
        response['errors'] = lib.error_catching(200)
    else:
        response["errors"] = lib.error_catching(404)

    return response


def edited_message(request: api.ValidJSON) -> dict:
    """Function changes the text and time in the database Message table.
    The value of the editedStatus column changes from None to True.

    Args:
        request (api.ValidJSON): client request - a set of data that was
        validated by "pydantic".

    Returns:
        dict: [description]
    """
    get_time = time()
    response = {
        "type": request.type,
        "data": None,
        'errors': None,
        'jsonapi': {
            'version': config.API_VERSION
            },
        'meta': None
        }

    if check_uuid_and_auth_id(request.data.user.uuid,
                              request.data.user.auth_id) is False:
        response['errors'] = lib.error_catching(401)
        return response

    dbquery = models.Message.select(models.Message.q.id ==
                                    request.data.message.id)
    # TODO
    # added a comparison of time contained in query
    # with time specified in Message database
    if dbquery.count():
        # changing in DB text, time and status
        dbquery[0].text = request.data.message.text
        dbquery[0].editedTime = get_time
        dbquery[0].editedStatus = True
        response['errors'] = lib.error_catching(200)
    else:
        response["errors"] = lib.error_catching(404)

    return response


def all_messages(request: api.ValidJSON) -> dict:
    """Function displays all messages of a specific flow retrieves them
    from the database and issues them as an array consisting of JSON

    Args:
        request (api.ValidJSON): client request - a set of data that was
        validated by "pydantic".

    Returns:
        dict: [description]
    """
    get_time = time()
    response = {
        "type": request.type,
        "data": None,
        'errors': None,
        'jsonapi': {
            'version': config.API_VERSION
            },
        'meta': None
        }

    if check_uuid_and_auth_id(request.data.user.uuid,
                              request.data.user.auth_id) is False:
        response["errors"] = lib.error_catching(401)
        return response

    dbquery = models.Message.select(models.Message.q.id > 0)
    if dbquery.count():
        messages = {}
        for i in dbquery:
            message = {
                i.id: {
                    "flowID": i.flowID,
                    "userID": i.userID,
                    "text": i.text,
                    "time": i.time,
                    "filePicture": i.filePicture,
                    "fileVideo": i.fileVideo,
                    "fileAudio": i.fileAudio,
                    "fileDocument": i.fileDocument,
                    "emoji": i.emoji,
                    "editedTime": i.editedTime,
                    "editedStatus": i.editedStatus
                    }
                }
            messages.update(message)

        data = {
            'time': get_time,
            'user': {
                'uuid': request.data.user.uuid,
                'auth_id': request.data.user.auth_id
            },
            'message': messages,
            'meta': None
            }
        response["data"] = data
        response['errors'] = lib.error_catching(200)
    else:
        response["errors"] = lib.error_catching(404)
    return response


def ping_pong(request: api.ValidJSON) -> dict:
    """The function generates a response to a client's request
    for communication between the server and the client.

    Args:
        request (api.ValidJSON): client request - a set of data that was
        validated by "pydantic".

    Returns:
        dict: [description]
    """
    get_time = time()
    response = {
        "type": request.type,
        "data": None,
        'errors': {
            'code': 200,
            'status': 'OK',
            'time': get_time,
            'detail': 'successfully'
            },
        'jsonapi': {
            'version': config.API_VERSION
            },
        'meta': None
        }
    return response


def errors(request: api.ValidJSON) -> dict:
    """Function handles cases when a request to server is not recognized by it.
    You get a standard answer type: error, which contains an object
    with a description of the error.

    Args:
        request (api.ValidJSON): client request - a set of data that was
        validated by "pydantic".

    Returns:
        dict: [description]
    """
    response = {
        'type': 'errors',
        'data': None,
        'errors': None,
        'jsonapi': {
            'version': config.API_VERSION
        },
        'meta': None
    }
    response['errors'] = lib.error_catching(405)
    return response
