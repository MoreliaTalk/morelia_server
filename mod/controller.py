import random
from time import time
from pydantic import ValidationError

from mod import models
from mod import config
from mod import api
from mod import lib

from sqlobject import SQLObjectIntegrityError
from sqlobject import SQLObjectNotFound


class ProtocolMethods:
    def __init__(self, request):
        self.response = api.ValidJSON()
        self.response.data = api.Data()
        self.response.data.flow: list = api.Flow()
        self.response.data.message: list = api.Message()
        #self.response.data.message.file = api.File()
        #self.response.data.message.from_flow = api.FromFlow()
        #self.response.data.message.from_user = api.MessageFromUser()
        #self.response.data.message.edited = api.EditedMessage()
        self.response.data.user: list = api.User()
        self.response.errors = api.Errors()
        self.response.jsonapi = api.Version()
        self.response.jsonapi.version = config.API_VERSION
        self.get_time = int(time())
        self.request = request
        try:
            self.request = api.ValidJSON.parse_raw(self.request)
        except ValidationError as error:
            self.response.type = "errors"
            self.response.errors = lib.error_catching(error)
        else:
            if __check_auth_token():
                if self.request.type == 'ping-pong':
                    self._ping_pong()
                elif self.request.type == 'register_user':
                    self._register_user()
                elif self.request.type == 'send_message':
                    self._send_message()
                elif self.request.type == 'all_flow':
                    self._all_flow()
                elif self.request.type == 'add_flow':
                    self._add_flow()
                elif self.request.type == 'all_messages':
                    self._all_messages()
                elif self.request.type == 'user_info':
                    self._user_info()
                elif self.request.type == 'auth':
                    self._authentification()
                elif self.request.type == 'delete_user':
                    self._delete_user()
                elif self.request.type == 'delete_message':
                    self._delete_message()
                elif self.request.type == 'edited_message':
                    self._edited_message()
                elif self.request.type == "get_update":
                    self._get_update()
                else:
                    self._errors()
            else:
                self.response.errors = lib.error_catching(401)

        return self.response.toJSON()

    def __check_auth_token(self) -> bool:
        """Function checks uuid and auth_id of user

        Args:
            uuid (int, requires): Unique User ID
            auth_id (str, requires): authentification ID

        Returns:
            bool
        """
        try:
            dbquery = models.User.select(models.User.q.uuid ==
                                         self.request.data.user.uuid).getOne()
        except SQLObjectIntegrityError, SQLObjectNotFound:
            pass
        else:
            if auth_id == dbquery.authId:
                return True
            else:
                return False

    def __check_login(self) -> bool:
        """Provides information about all personal settings of user
        (in a server-friendly form)

        Args:
            login (str, optional): user login

        Returns:
            Bool
        """
        try:
            dbquery = models.User.select(models.User.q.login ==
                                         self.request.data.user.login)
        except SQLObjectIntegrityError, SQLObjectNotFound:
            return False
        else:
            return True

    def _register_user(self):
        """The function registers the user who is not in the database.
        Note: This version also authentificate user, that exist in database
        Future version will return error if login exist in database

        Args:
            request (api.ValidJSON): client request - a set of data that was
            validated by "pydantic".

        Returns:
            dict: returns JSON reply to client
        """
        if __check_login() is False:
            generated = lib.Hash(password=self.request.data.user.password,
                                 salt=self.request.data.user.salt,
                                 key=self.request.data.user.key)

            models.User(uuid=random.getrandbits(64),
                        password=self.request.data.user.password,
                        hashPassword=generated.password_hash(),
                        salt=self.request.data.user.salt,
                        key=self.request.data.user.key,
                        login=self.request.data.user.login)
            self.response.errors = lib.ErrorsCatching(201).to_obj()
        else:
            # FIXME
            self.response.errors = lib.error_catching(409)

    def _get_update(self):
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
        for flow_id in self.request.data.flow:
            try:
                dbquery_flow = models.Flow.select(models.Flow.q.flowId ==
                                                  flow_id).getOne()
            except SQLObjectNotFound as flow_error:
                self.response.errors = lib.ErrorsCatching(404,
                                                          flow_error).to_dict()
            else:
                for flow in dbquery_flow:
                    dict_flow = {
                        "id": flow.flowId,
                        "time": flow.timeCreated,
                        "type": flow.flowType,
                        "title": flow.title,
                        "info": flow.info
                        }
                    self.response.data.flow.append(dict_flow)
            try:
                dbquery_message = models.Message.select(models.Message.q.flowID ==
                                                        flow_id)
            except SQLObjectNotFound as message_error:
                self.response.errors = lib.ErrorsCatching(404,
                                                          message_error).to_obj()
            else:
                for message in dbquery_message:
                    dict_message = {
                        "text": message.text,
                        "time": message.time,
                        "emoji": message.emoji,
                        "file": {
                            "picture": message.filePicture,
                            "video": message.fileVideo,
                            "audio": message.fileAudio,
                            "document": message.fileDocument
                            },
                        "from_user": {
                            "uuid": 123
                            },
                        "from_flow": {
                            "id": message.FlowID
                            },
                        "edited_message": {
                            "edited_time": message.editedTime,
                            "edited_status": message.editedStatus
                            }
                        }
                    self.response.data.message.append(dict_message)
        self.response.errors = lib.ErrorsCatching(200).to_obj()

    def _send_message(self):
        """The function saves user message in the database.

        Args:
            request (api.ValidJSON): client request - a set of data that was
            validated by "pydantic"

        Returns:
            dict: returns JSON reply to client
        """
        try:
            dbquery_flow = models.Flow.select(models.Flow.q.id ==
                                              self.request.data.flow.id).getOne()
        except SQLObjectNotFound as flow_error:
            self.response.errors = lib.ErrorsCatching(404, flow_error).to_dict()
        else:
            models.Message(text=self.request.data.message.text,
                           time=self.get_time,
                           filePicture=self.request.data.message.file.picture,
                           fileVideo=self.request.data.message.file.video,
                           fileAudio=self.request.data.message.file.audio,
                           fileDocument=self.request.data.message.file.audio,
                           emoji=self.request.data.message.emoji,
                           editedTime=self.request.data.message.edited_message.time,
                           editedStatus=self.request.data.message.edited_message.status,
                           user=self.request.data.user.uuid,
                           flow=self.request.data.flow.id)
            self.response.errors = lib.ErrorsCatching(200).to_dict()

    def _add_flow(self):
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
        except SQLObjectIntegrityError as flow_error:
            self.response.errors = lib.ErrorsCatching(404).to_dict()
        else:
            self.response.errors = lib.ErrorsCatching(200).to_dict()

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
        # FIXME
        self.response.errors = lib.error_catching(200)

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
        # FIXME
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
                'user': {
                    'uuid': dbquery[0].uuid,
                    'auth_id': dbquery[0].authId
                    },
                'meta': None
                }
            self.response.data = data
            # FIXME
            self.response.errors = lib.error_catching(200)
        else:
            # FIXME
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
                'user': {
                    'uuid': dbquery[0].uuid,
                    'login': dbquery[0].login
                    },
                'meta': None
                }
            dbquery[0].delete(dbquery[0].id)
            self.response.data = data
            # FIXME
            self.response.errors = lib.error_catching(200)
        else:

            self.response.errors = lib.error_catching(404)

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
            # FIXME
            self.response.errors = lib.error_catching(200)
        else:
            # FIXME
            self.response.errors = lib.error_catching(404)

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
            # FIXME
            self.response.errors = lib.error_catching(200)
        else:
            # FIXME
            self.response.errors = lib.error_catching(404)

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
                'user': {
                    'uuid': self.request.data.user.uuid,
                    'auth_id': self.request.data.user.auth_id
                },
                'message': messages,
                'meta': None
                }
            self.response.data = data
            # FIXME
            self.response.errors = lib.error_catching(200)
        else:
            # FIXME
            self.response.errors = lib.error_catching(404)

    def ping_pong(self):
        """The function generates a response to a client's request
        for communication between the server and the client.

        Args:
            request (api.ValidJSON): client request - a set of data that was
            validated by "pydantic".

        Returns:
            dict: [description]
        """
        # FIXME
        self.response.errors = lib.error_catching(200)

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
        self.response.type = "errors"
        # FIXME
        self.response.errors = lib.error_catching(405)
