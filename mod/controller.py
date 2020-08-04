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
    if dbpassword := get_userdata(request.data.user.login):
        if dbpassword == request.data.user.password:
            # TODO
            # generate authID: store and return to user
            response['errors']['code'] = 200
            response['errors']['status'] = 'Ok'
            response['errors']['detail'] = 'Authentificated'
            return response
        else:
            response['errors']['code'] = 401
            response['errors']['status'] = 'Unauthorized'
            response['errors']['detail'] = 'Bad username or password'
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


def all_message():
    pass


def add_flow(type_f, title_f, info_f):
    id_f = random.getrandbits(64)
    models.Flow(flowId=id_f,
                timeCreated=time(),
                flowType=type_f,
                title=title_f,
                info=info_f
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


def all_flow():
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


def delete_user(request: api.ValidJSON) -> dict:
    get_time = time()
    response = request.dict(include={'type'})
    try:
        dbquery = models.User.selectBy(uuid=request.data.user.uuid,
                                       auth_id=request.data.user.auth_id)
        dbquery_to_delete = models.Message.selectBy(id=request.data.message.id,
                                                    time=request.data.message.time,
                                                    )
    except IndexError as errors:
        print(errors)
        
    return response


def delete_message():
    pass


def edited_message():
    pass


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
