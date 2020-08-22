import random
from time import time

from mod import models
from mod import config
from mod import api
from mod import libhash


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

    if bool(dbquery.count()):
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


def check_uuid_and_auth_id(uuid: int, auth_id: str) -> dict:
    """Function checks the correctness of uuid and auth_id

    Args:
        uuid (int, requires): Unique User ID
        auth_id (str, requires): Authentication ID

    Returns:
        dict

    """
    get_time = time()
    dbquery = models.User.select(models.User.q.uuid == uuid)
    if bool(dbquery.count()):
        if auth_id == dbquery[0].authId:
            errors = {
                'code': 200,
                'status': 'OK',
                'time': get_time,
                'detail': 'successfully'
                }
        else:
            errors = {
                'code': 401,
                'status': 'Unauthorized',
                'time': get_time,
                'detail': 'Invalid auth_id'
                }
    else:
        errors = {
            'code': 401,
            'status': 'Unauthorized',
            'time': get_time,
            'detail': 'Invalid uuid'
            }
    return errors


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
    user = models.User.select(models.User.q.username == message['username'])
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
        user = models.User.select(models.User.q.uuid == data.userID)
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
    get_time = time()
    try:
        request = api.ValidJSON.parse_raw(request_json)
    except api.ValidationError:
        message = {
            'type': 'error',
            'errors': {
                'time': get_time,
                'status': 'Unsupported Media Type',
                'code': 415,
                'detail': 'JSON validation error'
                },
            'jsonapi': {
                'version': config.API_VERSION
                },
            'meta': None
            }
        return message
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
        return authentication(request)
    elif request.type == 'delete_user':
        return delete_user(request)
    elif request.type == 'delete_message':
        return delete_message(request)
    elif request.type == 'edited_message':
        return edited_message(request)
    elif request.type == "get_update":
        return get_update(request)
    else:
        message = {
            'type': request.type,
            'errors': {
                'time': get_time,
                'status': 'Method Not Allowed',
                'code': 405,
                'detail': 'Method not supported by server'
                },
            'jsonapi': {
                'version': config.API_VERSION
                },
            'meta': None
            }
        return message


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
    get_time = time()
    response = {
        "type": request.type,
        'data': None,
        'errors': {
            'status': 'Created',
            'code': 201,
            'detail': 'Registered successfully'
            },
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
        return response
    else:
        errors = {
            'code': 409,
            'status': 'error',
            'time': get_time,
            'detail': 'User already exists'
            }
        response['errors'] = errors
        return response


def filter_dbquery_by_time_from_and_to(dbquery, ot, do):
    response = []
    for db_data in dbquery:
        if db_data.time >= ot and db_data.time <= do:
            response.append(db_data)
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
        dict: [description]"""

    get_time = time()
    response = {
        "type": request.type,
        "data": {
            "time": get_time,
            "flow": {
                "id": request.data.flow.id
            }
        },
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

    if (errors :=
        check_uuid_and_auth_id(request.data.user.uuid,
                               request.data.user.auth_id))["code"] != 200:
        response["errors"] = errors
        return response

    dbquery_flow = models.Flow.select(models.Flow.q.flowId == request.data.flow.id)
    if bool(dbquery_flow.count()) is False:
        errors = {
            'code': 404,
            'status': 'Not Found',
            'time': get_time,
            'detail': 'Flow Not Found'
            }
        response["errors"] = errors
        return response

    # TODO нужно реализовать фильтрацию через SQLObject
    dbquery = []
    for db_data in models.Message.select(models.Message.q.flow == request.data.flow.id):
        if db_data.time >= request.data.time and db_data.time <= get_time:
            dbquery.append(db_data)

    if dbquery:
        messages = []
        for i in dbquery:
            message = {
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
            messages.append(message)

        data = {
            'time': get_time,
            'user': {
                'uuid': request.data.user.uuid,
                'auth_id': request.data.user.auth_id
            },
            'messages': messages,
            'meta': None
            }

        response["data"] = data
        return response
    else:
        errors = {
            'code': 404,
            'status': 'Not Found',
            'time': get_time,
            'detail': 'Messages Not Found'
            }
        response["errors"] = errors
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
    dbquery = models.User.select(
        models.User.q.username == request.data.user.login)
    # TODO
    # check existance of flow
    # check if user is member of flow
    # check can user send to channel
    # check is user banned to write in group
    models.Message(text=request.data.message.text,
                   userID=dbquery[0].uuid,
                   flowID=request.data.message.from_flow.id,
                   time=get_time)
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
    flow_id = random.getrandbits(64)
    models.Flow(flowId=flow_id,
                timeCreated=get_time,
                flowType=request.data.flow.type,
                title=request.data.flow.title,
                info=request.data.flow.info
                )
    response = {
        'type': request.type,
        'data': {
            'time': get_time,
            'meta': None
            },
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
    flow_list = []
    dbquery = models.Flow.select(models.Flow.q.id > 0)
    for flow in dbquery:
        data_flow = {
           "flowId": flow.flowId,
           "timeCreated": flow.timeCreated,
           "flowType": flow.flowType,
           "title": flow.title,
           "info": flow.info
        }
        flow_list.append(data_flow)
    response = {
        'type': request.type,
        'data': {
            'time': get_time,
            'flows': flow_list,
            'meta': None
            },
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
    dbquery = models.User.selectBy(uuid=request.data.user.uuid,
                                   auth_id=request.data.user.auth_id)
    if bool(dbquery.count()):
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
    else:
        errors = {
            'code': 401,
            'status': 'Unauthorized',
            'time': get_time,
            'detail': 'Unauthorized'
            }
        response["errors"] = errors
    return response


def authentication(request: api.ValidJSON) -> dict:
    """Performs authentication of registered client,
    with issuance of a unique hash number of connection session.
    During authentication password transmitted by client
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
    dbquery = models.User.select(models.User.q.login ==
                                 request.data.user.login)
    if bool(dbquery.count()):
        # Create an instance of the Hash class with
        # help of which we check the password and generating auth_id
        generator = libhash.Hash(dbquery[0].password,
                                 dbquery[0].salt,
                                 request.data.user.password,
                                 dbquery[0].key,
                                 dbquery[0].uuid)
        if generator.check_password():
            # generate a session hash ('auth_id') and immediately
            # add it to user parameters in database
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
        else:
            errors = {
                'code': 401,
                'status': 'Unauthorized',
                'time': get_time,
                'detail': 'Unauthorized'
                }
            response["errors"] = errors
    else:
        errors = {
            'code': 404,
            'status': 'Not Found',
            'time': get_time,
            'detail': 'User Not Found'
            }
        response["errors"] = errors

    return response


def delete_user(request: api.ValidJSON) -> dict:
    """Function irretrievably deletes the user from the database.

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
    check_user_in_db = models.User.selectBy(
        uuid=request.data.user.uuid, auth_id=request.data.user.auth_id)
    if bool(check_user_in_db.count()):
        dbquery = models.User.selectBy(login=request.data.user.login,
                                       password=request.data.user.password)
        if bool(dbquery.count()):
            data = {
                'user': {
                    'uuid': dbquery[0].uuid,
                    'login': dbquery[0].login
                    },
                'meta': None
                }
            dbquery[0].delete(dbquery[0].id)
            response["data"] = data
        else:
            errors = {
                'code': 404,
                'status': 'Not Found',
                'time': get_time,
                'detail': 'User Not Found'
                }
            response["errors"] = errors
    else:
        errors = {
            'code': 401,
            'status': 'Unauthorized',
            'time': get_time,
            'detail': 'Unauthorized'
            }
        response["errors"] = errors

    return response


def delete_message(request: api.ValidJSON) -> dict:
    """Function deletes the message from the database Message table by its ID.

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
    # TODO
    # check auth_id needs converting to single function
    check_user_in_db = models.User.selectBy(
        uuid=request.data.user.uuid, auth_id=request.data.user.auth_id)
    if bool(check_user_in_db.count()):
        dbquery = models.Message.select(
            models.User.q.messageID == request.data.message.id)
        if bool(dbquery.count()):
            dbquery[0].delete(dbquery[0].id)
        else:
            errors = {
                'code': 404,
                'status': 'Not Found',
                'time': get_time,
                'detail': 'Message Not Found'
                }
            response["errors"] = errors
    else:
        errors = {
            'code': 401,
            'status': 'Unauthorized',
            'time': get_time,
            'detail': 'Unauthorized'
            }
        response["errors"] = errors

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
    # TODO
    # check auth_id needs converting to single function
    check_user_in_db = models.User.selectBy(
        uuid=request.data.user.uuid, auth_id=request.data.user.auth_id)
    if bool(check_user_in_db.count()):
        dbquery = models.Message.select(
            models.User.q.messageID == request.data.message.id)
        # TODO
        # added a comparison of time contained in query
        # with time specified in Message database
        if bool(dbquery.count()):
            # changing in DB text, time and status
            dbquery[0].text = request.data.message.text
            dbquery[0].editedTime = get_time
            dbquery[0].editedStatus = True
        else:
            errors = {
                'code': 404,
                'status': 'Not Found',
                'time': get_time,
                'detail': 'User Not Found'
                }
            response["errors"] = errors
    else:
        errors = {
            'code': 401,
            'status': 'Unauthorized',
            'time': get_time,
            'detail': 'Unauthorized'
            }
        response["errors"] = errors

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

    if (errors :=
        check_uuid_and_auth_id(request.data.user.uuid,
                               request.data.user.auth_id))["code"] != 200:
        response["errors"] = errors
        return response

    dbquery = models.Message.select()
    if bool(dbquery.count()):
        messages = []
        for i in dbquery:
            message = {
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
            messages.append(message)

        data = {
            'time': get_time,
            'user': {
                'uuid': request.data.user.uuid,
                'auth_id': request.data.user.auth_id
            },
            'messages': messages,
            'meta': None
            }

        response["data"] = data
        return response
    else:
        errors = {
            'code': 404,
            'status': 'Not Found',
            'time': get_time,
            'detail': 'Messages Not Found'
            }
        response["errors"] = errors
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
