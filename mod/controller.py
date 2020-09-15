from time import time
from pydantic import ValidationError

from mod import models
from mod import config
from mod import api
from mod import lib

from sqlobject import SQLObjectIntegrityError
from sqlobject import SQLObjectNotFound

import random


class ProtocolMethods:
    def __init__(self, request):
        self.response = api.ValidJSON()
        self.response.data = api.Data()
        self.response.data.flow: list = api.Flow()
        self.response.data.message: list = api.Message()
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
            self.response.errors = lib.ErrorsCatching(error)
        else:
            if self.request.type == 'ping-pong':
                self._ping_pong()
            elif self.request.type == 'register_user':
                self._register_user()
            elif self.request.type == 'auth':
                self._authentification()
            else:
                if self.__check_auth_token():
                    if self.request.type == 'send_message':
                        self._send_message()
                    elif self.request.type == 'all_flow':
                        self._all_flow()
                    elif self.request.type == 'add_flow':
                        self._add_flow()
                    elif self.request.type == 'all_messages':
                        self._all_messages()
                    elif self.request.type == 'user_info':
                        self._user_info()
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
                    self.response.errors = lib.ErrorsCatching(401).to_dict()

    def get_response(self):
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
        except (SQLObjectIntegrityError, SQLObjectNotFound):
            return False
        else:
            if self.request.data.user.auth_id == dbquery.authId:
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
            models.User.select(models.User.q.login ==
                               self.request.data.user.login).getOne()
        except (SQLObjectIntegrityError, SQLObjectNotFound):
            return True
        else:
            return False

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
        if self.__check_login() is False:
            self.response.errors = lib.ErrorsCatching(409).to_dict()
        else:
            generated = lib.Hash(password=self.request.data.user.password,
                                 uuid=(gen_uuid := random.getrandbits(64)))
            models.User(uuid=gen_uuid,
                        hashPassword=generated.password_hash(),
                        login=self.request.data.user.login,
                        key=generated.get_key(),
                        salt=generated.get_salt(),
                        authId=(gen_auth_id := generated.auth_id())
                        )
            self.response.data.user.uuid = gen_uuid
            self.response.data.user.auth_id = gen_auth_id
            self.response.errors = lib.ErrorsCatching(201).to_obj()

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
                dbquery_message = models.Message.select(
                                                    models.Message.q.flowID ==
                                                    flow_id)
            except SQLObjectNotFound as message_error:
                self.response.errors = lib.ErrorsCatching(
                                                        404,
                                                        message_error).to_obj()
            else:
                for message in dbquery_message:
                    dict_message = {
                        "text": message.text,
                        "time": message.time,
                        "emoji": message.emoji,
                        "file_picture": message.filePicture,
                        "file_video": message.fileVideo,
                        "file_audio": message.fileAudio,
                        "file_document": message.fileDocument,
                        "from_user_uuid": 123,
                        "from_flow_id": message.FlowID,
                        "edited_time": message.editedTime,
                        "edited_status": message.editedStatus
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
            models.Flow.select(models.Flow.q.flowId ==
                               self.request.data.flow.id).getOne()
        except SQLObjectNotFound as flow_error:
            self.response.errors = lib.ErrorsCatching(404,
                                                      flow_error).to_dict()
        else:
            models.Message(text=self.request.data.message.text,
                           time=self.get_time,
                           filePicture=self.request.data.message.file_picture,
                           fileVideo=self.request.data.message.file_video,
                           fileAudio=self.request.data.message.file_audio,
                           fileDocument=self.request.data.message.file_audio,
                           emoji=self.request.data.message.emoji,
                           editedTime=self.request.data.message.edited_time,
                           editedStatus=self.request.data.
                           message.edited_status,
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
            self.response.errors = lib.ErrorsCatching(520,
                                                      flow_error).to_dict()
        else:
            self.response.errors = lib.ErrorsCatching(200).to_dict()

    def _all_flow(self):
        """Function allows to get a list of all flows and
        information about them from the database

        Args:
            request (api.ValidJSON): client request - a set of data that was
            validated by "pydantic".

        Returns:
            dict: [description]
        """
        try:
            dbquery = models.Flow.select(models.Flow.q.id > 0)
        except SQLObjectNotFound:
            self.response.errors = lib.ErrorsCatching(404).to_dict()
        for i in dbquery:
            element_in_database = {
                "id": i.flowId,
                "time": i.timeCreated,
                "type": i.flowType,
                "title": i.title,
                "info": i.info
                }
            self.response.data.flow.append(element_in_database)
        self.response.errors = lib.ErrorsCatching(200)

    def _user_info(self):
        """Provides information about all personal settings of user.

        Args:
            request (api.ValidJSON): client request - a set of data that was
            validated by "pydantic".

        Returns:
            dict: [description]
        """
        try:
            dbquery = models.User.select(models.User.q.uuid ==
                                         self.request.data.user.uuid).getOne()
        except SQLObjectNotFound:
            self.response.errors = lib.ErrorsCatching(404).to_dict()
        else:
            user_info = {
                'uuid': dbquery.uuid,
                'login': dbquery.login,
                'password': dbquery.password,
                'username': dbquery.username,
                'is_bot': dbquery.isBot,
                'auth_id': dbquery.authId,
                'email': dbquery.email,
                'avatar': dbquery.avatar,
                'bio': dbquery.bio
                }
            self.response.data.user.append(user_info)
            self.response.errors = lib.ErrorsCatching(200)

    def _authentification(self):
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
        try:
            dbquery = models.User.selectBy(
                                            login=self.request.data.user.login
                                            ).getOne()
        except (SQLObjectIntegrityError, SQLObjectNotFound):
            self.response.errors = lib.ErrorsCatching(404)
        else:
            generator = lib.Hash(password=self.request.data.user.password,
                                 uuid=dbquery.uuid,
                                 salt=dbquery.salt,
                                 key=dbquery.key,
                                 hash_password=dbquery.hashPassword
                                 )

            if generator.check_password():
                dbquery.authId = generator.auth_id()
                self.response.data.user.uuid = dbquery.uuid
                self.response.data.user.auth_id = dbquery.authId
                self.response.errors = lib.ErrorsCatching(200)
            else:
                self.response.errors = lib.ErrorsCatching(401)

    def _delete_user(self):
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
            self.response.errors = lib.ErrorsCatching(200)
        else:

            self.response.errors = lib.ErrorsCatching(404)

    def _delete_message(self):
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
            self.response.errors = lib.ErrorsCatching(200)
        else:
            # FIXME
            self.response.errors = lib.ErrorsCatching(404)

    def _edited_message(self):
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
            self.response.errors = lib.ErrorsCatching(200)
        else:
            self.response.errors = lib.ErrorsCatching(404)

    def _all_messages(self):
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
            self.response.errors = lib.ErrorsCatching(200)
        else:
            self.response.errors = lib.ErrorsCatching(404)

    def _ping_pong(self):
        """The function generates a response to a client's request
        for communication between the server and the client.

        Args:
            request (api.ValidJSON): client request - a set of data that was
            validated by "pydantic".

        Returns:
            dict: [description]
        """
        # FIXME
        self.response.errors = lib.ErrorsCatching(200)

    def _errors(self):
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
        self.response.errors = lib.ErrorsCatching(405)
