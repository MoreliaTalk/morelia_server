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


class ProtocolMethods:
    def __init__(self, json_request):
        self.response = api.ValidJSON()
        self.response.data = api.Data()
        self.response.data.message = api.Message()
        self.response.data.message.file = api.File()
        self.response.data.message.from_flow = api.FromFlow()
        self.response.data.message.from_user = api.MessageFromUser()
        self.response.data.message.edited = api.EditedMessage()
        self.response.data.user = api.User()
        self.response.errors = api.Errors()
        self.response.jsonapi = api.Version()
        self.response.jsonapi.version = config.API_VERSION
        self.get_time = int(time())
        self.json_request = json_request

    def serve_request(self) -> dict:
        """The function try serve user request and return result status.

        Args:
            No args.

        Returns:
            Response for sending to user  - successfully served
            (error response - if any kind of problems)
        """
        try:
            self.request = api.ValidJSON.parse_raw(self.json_request)
        except ValidationError as error:
            self.response.type = "errors"
            self.response.errors = lib.error_catching(error)
        else:
            if check_uuid_and_auth_id(self.request.data.user.uuid,
                                      self.request.data.user.auth_id):
                if self.request.type == 'ping-pong':
                    self.ping_pong()
                elif self.request.type == 'register_user':
                    self.register_user()
                elif self.request.type == 'send_message':
                    self.send_message()
                elif self.request.type == 'all_flow':
                    self.all_flow()
                elif self.request.type == 'add_flow':
                    self.add_flow()
                elif self.request.type == 'all_messages':
                    self.all_messages()
                elif self.request.type == 'user_info':
                    self.user_info()
                elif self.request.type == 'auth':
                    self.authentification()
                elif self.request.type == 'delete_user':
                    self.delete_user()
                elif self.request.type == 'delete_message':
                    self.delete_message()
                elif self.request.type == 'edited_message':
                    self.edited_message()
                elif self.request.type == "get_update":
                    self.get_update()
                else:
                    self.errors()
            else:
                self.response.errors = lib.error_catching(401)

        return self.response.toJSON()

    def register_user(self):
        """The function registers the user who is not in the database.
        Note: This version also authentificate user, that exist in database
        Future version will return error if login exist in database

        Args:
            request (api.ValidJSON): client request - a set of data that was
            validated by "pydantic".

        Returns:
            dict: returns JSON reply to client
        """
        if user_info_for_server(login=self.request.data.user.login) is None:
            # TODO
            # generate authID: store and return to user
            # generate salt, and create hash password
            userID = random.getrandbits(64)
            models.User(uuid=userID,
                        password=self.request.data.user.password,
                        login=self.request.data.user.login,
                        username=self.request.data.user.login)
            self.response.errors = lib.error_catching(201)
        else:
            # TODO поменять тип ошибки на 409
            self.response.errors = lib.error_catching(400)

    def get_update(self):
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
        dbquery_flow = models.Flow.select(models.Flow.q.flowId ==
                                          self.request.data.flow.id)
        if dbquery_flow.count():
            data = {
                "time": self.get_time,
                "flow": {
                    "id": dbquery_flow[0].flowId,
                    "time": dbquery_flow[0].timeCreated,
                    "type": dbquery_flow[0].flowType,
                    "title": dbquery_flow[0].title,
                    "info": dbquery_flow[0].info
                    }
                }
            self.response.data = data

            dbquery_message = models.Message.select(
                models.Message.q.flowID == self.request.data.flow.id)

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
                        'uuid': self.request.data.user.uuid,
                        'auth_id': self.request.data.user.auth_id
                        },
                    'messages': messages,
                    'meta': None
                    }
                self.response["data"] = data
                self.response['errors'] = lib.error_catching(200)

            else:
                self.response["errors"] = lib.error_catching(404, "Message\
                                                                Not Found")
        else:
            self.response['errors'] = lib.error_catching(404, 'Flow\
                                                            Not Found')

    def send_message(self):
        """The function saves user message in the database.

        Args:
            request (api.ValidJSON): client request - a set of data that was
            validated by "pydantic"

        Returns:
            dict: returns JSON reply to client
        """

        check_user_in_db = models.User.select(models.User.q.uuid ==
                                              self.request.data.user.uuid)
        check_flow_in_db = models.Flow.select(models.Flow.q.id ==
                                              self.request.data.flow.id)
        models.Message(text=self.request.data.message.text,
                       time=self.get_time,
                       user=check_user_in_db,
                       flow=check_flow_in_db)

        self.response.errors = lib.error_catching(200)

    def add_flow(self):
        """Function allows you to add a new flow to the database

        Args:
            request (api.ValidJSON): client request - a set of data that was
            validated by "pydantic".

        Returns:
            dict: [description]
        """
        flow_id = random.getrandbits(64)
        try:
            models.Flow(flowId=flow_id,
                        timeCreated=self.get_time,
                        flowType=self.request.data.flow.type,
                        title=self.request.data.flow.title,
                        info=self.request.data.flow.info)
        except Exception as error:
            self.response.errors = lib.error_catching(error)
        else:
            self.response.errors = lib.error_catching(200)

    def all_flow(self):
        """Function allows to get a list of all flows and
        information about them from the database

        Args:
            request (api.ValidJSON): client request - a set of data that was
            validated by "pydantic".

        Returns:
            dict: [description]
        """
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
                'time': self.get_time,
                'flow': flows,
                'meta': None
                }
        self.response.data = data
        self.response.errors. = lib.error_catching(200)

    def user_info(self):
        """Provides information about all personal settings of user.

        Args:
            request (api.ValidJSON): client request - a set of data that was
            validated by "pydantic".

        Returns:
            dict: [description]
        """
        dbquery = models.User.selectBy(uuid=self.request.data.user.uuid,
                                       authId=self.request.data.user.auth_id)
        data = {
            'time': self.get_time,
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
        self.response.data = data
        self.response.errors = lib.error_catching(200)

    def authentification(self):
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
        dbquery = models.User.selectBy(
                                    login=self.request.data.user.login,
                                    password=self.request.data.user.password)
        if dbquery.count():
            # TODO После внесения изменений в протокол
            # переделать алгоритм авторизации
            generator = lib.Hash(dbquery[0].password,
                                 dbquery[0].salt,
                                 uuid=dbquery[0].uuid)
            dbquery[0].authId = generator.auth_id()
            data = {
                'time': self.get_time,
                'user': {
                    'uuid': dbquery[0].uuid,
                    'auth_id': dbquery[0].authId
                    },
                'meta': None
                }
            self.response.data = data
            self.response.errors = lib.error_catching(200)
        else:
            self.response.errors = lib.error_catching(404)

    def delete_user(self):
        """Function irretrievably deletes the user from the database.

        Args:
            request (api.ValidJSON): client request - a set of data that was
            validated by "pydantic".

        Returns:
            dict: [description]
        """
        dbquery = models.User.selectBy(
                                    login=self.request.data.user.login,
                                    password=self.request.data.user.password)
        if dbquery.count():
            data = {
                'time': self.get_time,
                'user': {
                    'uuid': dbquery[0].uuid,
                    'login': dbquery[0].login
                    },
                'meta': None
                }
            dbquery[0].delete(dbquery[0].id)
            self.response["data"] = data
            self.response['errors'] = lib.error_catching(200)
        else:
            self.response["errors"] = lib.error_catching(404)

    def delete_message(self):
        """Function deletes the message from the database Message table by its ID.

        Args:
            request (api.ValidJSON): client request - a set of data that was
            validated by "pydantic".

        Returns:
            dict: [description]
        """

        dbquery = models.Message.select(models.Message.q.id ==
                                        self.request.data.message.id)
        if dbquery.count():
            dbquery[0].delete(dbquery[0].id)
            self.response['errors'] = lib.error_catching(200)
        else:
            self.response["errors"] = lib.error_catching(404)

    def edited_message(self):
        """Function changes the text and time in the database Message table.
        The value of the editedStatus column changes from None to True.

        Args:
            request (api.ValidJSON): client request - a set of data that was
            validated by "pydantic".

        Returns:
            dict: [description]
        """

        dbquery = models.Message.select(models.Message.q.id ==
                                        self.request.data.message.id)
        # TODO
        # added a comparison of time contained in query
        # with time specified in Message database
        if dbquery.count():
            # changing in DB text, time and status
            dbquery[0].text = self.request.data.message.text
            dbquery[0].editedTime = self.get_time
            dbquery[0].editedStatus = True
            self.response['errors'] = lib.error_catching(200)
        else:
            self.response["errors"] = lib.error_catching(404)

    def all_messages(self):
        """Function displays all messages of a specific flow retrieves them
        from the database and issues them as an array consisting of JSON

        Args:
            request (api.ValidJSON): client request - a set of data that was
            validated by "pydantic".

        Returns:
            dict: [description]
        """

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
                'time': self.get_time,
                'user': {
                    'uuid': self.request.data.user.uuid,
                    'auth_id': self.request.data.user.auth_id
                },
                'message': messages,
                'meta': None
                }
            self.response["data"] = data
            self.response['errors'] = lib.error_catching(200)
        else:
            self.response["errors"] = lib.error_catching(404)

    def ping_pong(self):
        """The function generates a response to a client's request
        for communication between the server and the client.

        Args:
            request (api.ValidJSON): client request - a set of data that was
            validated by "pydantic".

        Returns:
            dict: [description]
        """
        self.response['errors'] = lib.error_catching(200)

    def errors(self):
        """Function handles cases when a request to server is not recognized by it.
        You get a standard answer type: error, which contains an object
        with a description of the error.

        Args:
            request (api.ValidJSON): client request - a set of data that was
            validated by "pydantic".

        Returns:
            dict: [description]
        """
        self.response["type"] = "errors"
        self.response['errors'] = lib.error_catching(405)
