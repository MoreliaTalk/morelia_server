import random
from time import time

from mod import models
from mod import config
from mod import api
from mod import libhash


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


def register_user(request: api.ValidJSON) -> dict:
    """The function registers the user who is not in the database.

    Note: This version also authentificate user, that exist in database
    Future version will return error if login exist in database

    Args:
        request (class ValidJSON): required

    Returns:
        Dict: returns JSON reply to client
    """
    response = {
        'type': 'register_user',
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
    # TODO: пофиксить строку
    if user_info_for_server(login=request.data.user.login):
        response['errors']['code'] = 409
        response['errors']['status'] = 'error'
        response['errors']['detail'] = 'User already exists'
        return response
    else:
        # TODO
        # generate authID: store and return to user
        # generate salt, and create hash password
        userID = random.getrandbits(64)
        models.User(uuid=userID,
                    password=request.data.user.password,
                    login=request.data.user.login,
                    username=request.data.user.login)
        return response


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


def get_update():
    pass


def send_message(request: api.ValidJSON) -> dict:
    """The function saves user message in the database.

    Args:
        request (class ValidJSON): required

    Returns:
        Dict: returns JSON reply to client
    """
    get_time = time()
    response = {
            'type': 'send_message',
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
    flowid = request.data.message.from_flow.id
    user = models.User.select(models.User.q.username == request.data.user.login)
    # TODO
    # check existance of flow
    # check if user is member of flow
    # check can user send to channel
    # check is user banned to write in group
    models.Message(text=request.data.message.text,
                   userID=user[0].uuid,
                   flowID=flowid,
                   time=get_time)
    return response


def add_flow(request):
    id_f = random.getrandbits(64)
    models.Flow(flowId=id_f,
                timeCreated=time(),
                flowType=request.data.type,
                title=request.data.title,
                info=request.data.info
                )
    message = {
        'type': 'add_flow',
        'data': {
            'time': time(),
            'meta': None
        },
        'errors': {
            'code': 200,
            'status': 'OK',
            'time': 1594492370,
            'detail': 'successfully'
        },
        'jsonapi': {
            'version': '1.0'
        },
        'meta': None
    }
    return message


def all_flow(request):
    flow_list = []
    dbquery = models.Flow.select(models.Flow.q.id > 0)
    for db_flow in dbquery:
        data_flow = {
           "flowId": db_flow.flowId,
           "timeCreated": db_flow.timeCreated,
           "flowType": db_flow.flowType,
           "title": db_flow.title,
           "info": db_flow.info
        }
        flow_list.append(data_flow)
    message = {
        'type': 'all_flow',
        'data': {
            'time': time(),
            'flows': flow_list,
            'meta': None
        },
        'errors': {
            'code': 200,
            'status': 'OK',
            'time': 1594492370,
            'detail': 'successfully'
        },
        'jsonapi': {
            'version': '1.0'
        },
        'meta': None
    }
    return message


def user_info(request: api.ValidJSON) -> dict:
    """Provides information about all personal settings of user.

    Args:
        request (api.ValidJSON): client request - a set of data that was
        validated by "pydantic".

    Returns:
        dict: [description]
    """
    get_time = time()
    response = request.dict(include={'type'})
    jsonapi = {
        'jsonapi': {
            'version': config.API_VERSION
            },
        'meta': None
        }
    dbquery = models.User.select(models.User.q.uuid == request.data.user.uuid)
    if bool(dbquery.count()):
        # Create an instance of the Hash class with
        # help of which we check the password.
        generator = libhash.Hash(dbquery[0].password,
                                 dbquery[0].salt,
                                 request.data.user.password,
                                 dbquery[0].key,
                                 dbquery[0].uuid)
        if generator.check_password():
            data = {
                'data': {
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
                    },
                'errors': {
                    'code': 200,
                    'status': 'OK',
                    'time': get_time,
                    'detail': 'successfully'
                    }
                }
            response.update(data)
        else:
            errors = {
                'errors': {
                    'code': 401,
                    'status': 'Unauthorized',
                    'time': get_time,
                    'detail': 'Unauthorized'
                    }
            }
            response.update(errors)
    else:
        errors = {
            'errors': {
                'code': 404,
                'status': 'Not Found',
                'time': get_time,
                'detail': 'User Not Found'
            }
        }
        response.update(errors)

    return response.update(jsonapi)


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
    response = request.dict(include={'type'})
    jsonapi = {
        'jsonapi': {
            'version': config.API_VERSION
        },
        'meta': None
    }
    dbquery = models.User.select(models.User.q.login == request.data.user.login)
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
                'data': {
                    'time': get_time,
                    'user': {
                        'uuid': dbquery[0].uuid,
                        'auth_id': dbquery[0].authId
                        },
                    'meta': None
                    },
                'errors': {
                    'code': 200,
                    'status': 'OK',
                    'time': get_time,
                    'detail': 'successfully'
                    }
                }
            response.upadate(data)
        else:
            errors = {
                'errors': {
                    'code': 401,
                    'status': 'Unauthorized',
                    'time': get_time,
                    'detail': 'Unauthorized'
                    }
                }
            response.update(errors)
    else:
        errors = {
            'errors': {
                'code': 404,
                'status': 'Not Found',
                'time': get_time,
                'detail': 'User Not Found'
                }
            }
        response.update(errors)

    return response.update(jsonapi)


def delete_user():
    pass


def delete_message():
    pass


def edited_message():
    pass


def user_info_for_server(uuid=None, login=None) -> dict:
    """Provides information about all personal settings of user(in a server-friendly form).

    Args:
        uuid - Unique User ID(int)
            or
        login(str)

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
    """
    This function checks the correctness of uuid and auth_id
    Args:
        uuid - Unique User ID(int)
        auth_id - AUTHentication ID(str)

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


def all_messages(request: api.ValidJSON) -> dict:
    """
    This function displays all messages of a specific chat(flow)
    Retrieves them from the database and issues them as an array consisting of JSON

    Args:request

    Returns:dict
    """
    get_time = time()
    template = {
        'type': request.type,
        'data': None,
        'errors': None,
        'jsonapi': {
            'version': config.API_VERSION
        },
        'meta': None
        }

    if (errors := check_uuid_and_auth_id(request.data.user.uuid, request.data.user.auth_id))["code"] != 200:
        template["errors"] = errors
        return template

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

        template["data"] = data
        template["errors"] = errors
        return template


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
    response = request.dict(include={type})
    data = {
        'data': None,
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
    return response.update(data)
