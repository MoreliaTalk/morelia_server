from pydantic import ValidationError
from time import time
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
        self.response.data.flow = list()
        self.response.data.message = list()
        self.response.data.user = list()
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
            self.response.type = self.request.type
            if self.request.type == 'ping-pong':  #
                self._ping_pong()
            elif self.request.type == 'register_user':  #
                self._register_user()
            elif self.request.type == 'auth':  #
                self._authentification()
            elif self.request.type == 'user_info':
                self._user_info()
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
            dbquery = models.User.select(
                        models.User.q.uuid == self.request.data.user[0].uuid
                                    ).getOne()

        except (SQLObjectIntegrityError, SQLObjectNotFound):
            return False
        else:
            if self.request.data.user[0].auth_id == dbquery.authId:
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
                               self.request.data.user[0].login).getOne()
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
            generated = lib.Hash(password=self.request.data.user[0].password,
                                 uuid=(gen_uuid := random.getrandbits(64)))

            models.User(uuid=gen_uuid,
                        hashPassword=generated.password_hash(),
                        login=self.request.data.user[0].login,
                        key=generated.get_key(),
                        salt=generated.get_salt(),
                        authId=(gen_auth_id := generated.auth_id()))
            self.response.data.user.append(api.User())
            self.response.data.user[0].uuid = gen_uuid
            self.response.data.user[0].auth_id = gen_auth_id
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
        for flowq in self.request.data.flow:
            try:
                dbquery_message = models.Message.select(
                                models.Message.q.flow == flowq.id and
                                models.Message.q.time > self.request.data.time
                                        )
            except SQLObjectNotFound as message_error:
                self.response.errors = lib.ErrorsCatching(
                                                        404,
                                                        message_error)
            else:
                for message in dbquery_message:

                    message_el = api.Message()

                    message_el.text = message.text
                    message_el.time = message.time
                    message_el.emoji = message.emoji
                    message_el.file_picture = message.filePicture
                    message_el.file_video = message.fileVideo
                    message_el.file_audio = message.fileAudio
                    message_el.file_document = message.fileDocument
                    message_el.from_user_uuid = message.userID
                    message_el.from_flow_id = message.FlowID
                    message_el.edited_status = message.editedStatus

                    self.response.data.message.append(message_el)
        try:
            dbquery_flow = models.Flow.select(
                        models.Flow.q.timeCreated == self.request.data.time)
        except SQLObjectNotFound as flow_error:
            self.response.errors = lib.ErrorsCatching(404,
                                                      flow_error)
        else:
            for flow in dbquery_flow:
                flow_el = api.Flow()
                flow_el.id = flow.flowId
                flow_el.time = flow.timeCreated
                flow_el.type = flow.flowType
                flow_el.title = flow.title
                flow_el.info = flow.info

                self.response.data.flow.append(flow_el)
        self.response.errors = lib.ErrorsCatching(200)

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
                               self.request.data.flow[0].id).getOne()
        except SQLObjectNotFound as flow_error:
            self.response.errors = lib.ErrorsCatching(404,
                                                      flow_error).to_dict()
        else:
            models.Message(
                        text=self.request.data.message[0].text,
                        time=self.get_time,
                        filePicture=self.request.data.message[0].file_picture,
                        fileVideo=self.request.data.message[0].file_video,
                        fileAudio=self.request.data.message[0].file_audio,
                        fileDocument=self.request.data.message[0].file_audio,
                        emoji=self.request.data.message[0].emoji,
                        editedTime=self.request.data.message[0].edited_time,
                        editedStatus=self.request.data.
                        message[0].edited_status,
                        user=self.request.data.user[0].uuid,
                        flow=self.request.data.flow[0].id
                        )
            self.response.errors = lib.ErrorsCatching(200).to_dict()

    def _add_flow(self):
        """Function allows you to add a new flow to the database

        Args:
            request (api.ValidJSON): client request - a set of data that was
            validated by "pydantic".

        Returns:
            dict: [description]
        """
        try:
            flow_id = random.getrandbits(64)
            models.Flow(flowId=flow_id,
                        timeCreated=self.get_time,
                        flowType=self.request.data.flow[0].type,
                        title=self.request.data.flow[0].title,
                        info=self.request.data.flow[0].info)
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
            element = api.Flow()
            element.id = i.flowId
            element.time = i.timeCreated
            element.type = i.flowType
            element.title = i.title
            element.info = i.info
            self.response.data.flow.append(element)

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
            dbquery = models.User.select(
                models.User.q.uuid == self.request.data.user[0].uuid).getOne()

        except SQLObjectNotFound:
            self.response.errors = lib.ErrorsCatching(404).to_dict()
        else:
            user_info = api.User()
            user_info.uuid = dbquery.uuid
            user_info.login = dbquery.login
            user_info.username = dbquery.username
            user_info.is_bot = dbquery.isBot
            user_info.email = dbquery.email
            user_info.avatar = dbquery.avatar
            user_info.bio = dbquery.bio
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
                                        login=self.request.data.user[0].login
                                            ).getOne()
        except (SQLObjectIntegrityError, SQLObjectNotFound):
            self.response.errors = lib.ErrorsCatching(404)
        else:
            generator = lib.Hash(password=self.request.data.user[0].password,
                                 uuid=dbquery.uuid,
                                 salt=dbquery.salt,
                                 key=dbquery.key,
                                 hash_password=dbquery.hashPassword
                                 )

            if generator.check_password():
                dbquery.authId = generator.auth_id()
                self.response.data.user.append(api.User())
                self.response.data.user[0].uuid = dbquery.uuid
                self.response.data.user[0].auth_id = dbquery.authId
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
        try:
            dbquery = models.User.selectBy(
                                    uuid=self.request.data.user[0].uuid
                                          ).getOne()
        except SQLObjectNotFound as er_not_found:
            self.response.errors = lib.ErrorsCatching(404, er_not_found)
        else:
            dbquery.delete(dbquery.id)
            self.response.errors = lib.ErrorsCatching(200)

    def _delete_message(self):
        """Function deletes the message from the database Message table by its ID.

        Args:
            request (api.ValidJSON): client request - a set of data that was
            validated by "pydantic".

        Returns:
            dict: [description]
        """
        try:
            dbquery = models.Message.select(
                    models.Message.q.id == self.request.data.message[0].id
                    ).getOne()

        except SQLObjectNotFound as er_not_found:
            self.response.errors = lib.ErrorsCatching(404, er_not_found)
        else:
            dbquery.delete(dbquery.id)
            self.response.errors = lib.ErrorsCatching(200)

    def _edited_message(self):
        """Function changes the text and time in the database Message table.
        The value of the editedStatus column changes from None to True.

        Args:
            request (api.ValidJSON): client request - a set of data that was
            validated by "pydantic".

        Returns:
            dict: [description]
        """
        # TODO
        # added a comparison of time contained in query
        # with time specified in Message database
        try:
            dbquery = models.Message.select(models.Message.q.id ==
                                            self.request.data.message[0].id
                                            ).getOne()
        except SQLObjectNotFound as er_not_found:
            self.response.errors = lib.ErrorsCatching(404, er_not_found)
        else:
            # changing in DB text, time and status
            dbquery.text = self.request.data.message[0].text
            dbquery.editedTime = self.get_time
            dbquery.editedStatus = True
            self.response.errors = lib.ErrorsCatching(200)

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
            for i in dbquery:
                message = api.Message()
                message.from_flow_id = i.flowID
                message.from_user_uuid = i.userID
                message.text = i.text
                message.time = i.time
                message.file_picture = i.filePicture
                message.file_video = i.fileVideo
                message.file_audio = i.fileAudio
                message.file_document = i.fileDocument
                message.emoji = i.emoji
                message.edited_time = i.editedTime
                message.edited_status = i.editedStatus
                self.response.data.message.append(message)

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
