import random
from os import urandom
from time import time
from typing import Optional, Union

from pydantic import ValidationError
from sqlobject import AND
from sqlobject import SQLObjectIntegrityError
from sqlobject import SQLObjectNotFound
from sqlobject import dberrors

from mod import api
from mod import config
from mod import lib
from mod import models


class ProtocolMethods:
    """The class is responsible for processing requests and forming answers
    according to "Udav" protocol. Protocol version and it's actual description:
    https://github.com/MoreliaTalk/morelia_protocol/blob/master/README.md
    """
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

        try:
            self.request = api.ValidJSON.parse_obj(request)
        except ValidationError as error:
            self.response.type = "errors"
            self.__catching_error(415, str(error))
        else:
            self.response.type = self.request.type
            if self.request.type == 'register_user':
                self._register_user()
            elif self.request.type == 'auth':
                self._authentification()
            else:
                if self.__check_auth_token(self.request.data.user[0].uuid,
                                           self.request.data.user[0].auth_id):
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
                    elif self.request.type == "ping-pong":
                        self._ping_pong()
                    elif self.request.type == 'user_info':
                        self._user_info()
                    else:
                        self._errors()
                else:
                    self.__catching_error(401)

    def get_response(self):
        """Function generates a JSON-object containing result
        of an instance of ProtocolMethod class.

        """
        return self.response.toJSON()

    def __check_auth_token(self, uuid: str, auth_id: str) -> bool:
        """Function checks uuid and auth_id of user

        Args:
            uuid (int, requires): Unique User ID
            auth_id (str, requires): authentification ID

        Returns:
            True if successful
            False if unsuccessful
        """
        try:
            dbquery = models.UserConfig.selectBy(uuid=uuid).getOne()
        except (dberrors.OperationalError,
                SQLObjectIntegrityError, SQLObjectNotFound):
            return False
        else:
            if auth_id == dbquery.authId:
                return True
            else:
                return False

    def __check_login(self, login: str) -> bool:
        """Provides information about all personal settings of user
        (in a server-friendly form)

        Args:
            login (str, optional): user login

        Returns:
            True if there is such a user
            False if no such user exists
        """
        try:
            models.UserConfig.selectBy(login=login).getOne()
        except (SQLObjectIntegrityError, SQLObjectNotFound):
            return False
        else:
            return True

    def __catching_error(self, code: Union[int, str],
                         add_info: Optional[str] = None) -> None:
        """Function catches errors in the "try...except" content.
        Result is 'dict' with information about the code, status,
        time and detailed description of the error that has occurred.
        For errors like Exception and other unrecognized errors,
        code "520" and status "Unknown Error" are used.
        Function also automatically logs the error.

        Args:
            code (Union[int, str]): Error code or type and exception
            description.
            add_info (Optional[str], optional): Additional information
            to be added. The 'Exception' field is not used for exceptions.
            Defaults to None.

        Returns:
            dict: returns 'dict' according to the protocol,
                like: {
                    'code': 200,
                    'status': 'Ok',
                    'time': 123456545,
                    'detail': 'successfully'
                    }
        """
        if code in config.DICT_ERRORS:
            if add_info is None:
                add_info = config.DICT_ERRORS[code]['detail']
            self.response.errors.code = code
            self.response.errors.status = config.DICT_ERRORS[code]['status']
            self.response.errors.time = self.get_time
            self.response.errors.detail = add_info
        else:
            self.response.errors.code = 520
            self.response.errors.status = 'Unknown Error'
            self.response.errors.time = self.get_time
            self.response.errors.detail = code

    def _register_user(self):
        """The function registers the user who is not in the database.
        Note: This version also authentificate user, that exist in database
        Future version will return error if login exist in database

        """
        # FIXME после замены uuid на UUID из питоньего модуля
        random.seed(urandom(64))
        gen_uuid = random.randrange(10000, 999999999999)
        if self.__check_login(self.request.data.user[0].login):
            self.__catching_error(409)
        else:
            generated = lib.Hash(password=self.request.data.user[0].password,
                                 uuid=gen_uuid)
            models.UserConfig(uuid=gen_uuid,
                              password=self.request.data.user[0].password,
                              hashPassword=generated.password_hash(),
                              login=self.request.data.user[0].login,
                              username=self.request.data.user[0].username,
                              email=self.request.data.user[0].email,
                              key=generated.get_key(),
                              salt=generated.get_salt(),
                              authId=(gen_auth_id := generated.auth_id()))
            user = api.User()
            user.uuid = gen_uuid
            user.auth_id = gen_auth_id
            self.response.data.user.append(user)
            self.__catching_error(201)

    def _get_update(self):
        """The function displays messages of a specific flow,
        from the timestamp recorded in the request to the server timestamp,
        retrieves them from the database
        and issues them as an array consisting of JSON

        """
        # TODO внеести измнения в протокол, добавить фильтр
        # по дате создания пользователя
        dbquery_user = models.UserConfig.selectBy()
        dbquery_flow = models.Flow.select(models.Flow.q.timeCreated >=
                                          self.request.data.time)
        dbquery_message = models.Message.select(models.Message.q.time >=
                                                self.request.data.time)
        if dbquery_message.count():
            for element in dbquery_message:
                message = api.Message()
                message.text = element.text
                message.time = element.time
                message.emoji = element.emoji
                message.file_picture = element.filePicture
                message.file_video = element.fileVideo
                message.file_audio = element.fileAudio
                message.file_document = element.fileDocument
                message.from_user_uuid = element.userID
                message.from_flow_id = element.flowID
                message.edited_status = element.editedStatus
                self.response.data.message.append(message)
        elif dbquery_flow.count():
            for element in dbquery_flow:
                flow = api.Flow()
                flow.id = element.flowId
                flow.time = element.timeCreated
                flow.type = element.flowType
                flow.title = element.title
                flow.info = element.info
                self.response.data.flow.append(flow)
        elif dbquery_user.count():
            for element in dbquery_user:
                user = api.User()
                user.uuid = element.uuid
                user.username = element.username
                user.is_bot = element.isBot
                user.avatar = element.avatar
                user.bio = element.bio
                self.response.data.user.append(user)
        else:
            self.__catching_error(404)
        self.__catching_error(200)

    def _send_message(self):
        """The function saves user message in the database.

        """
        try:
            models.Flow.selectBy(flowId=self.request.data.flow[0].id).getOne()
        except SQLObjectNotFound as flow_error:
            self.__catching_error(404, str(flow_error))
        else:
            models.Message(text=self.request.data.message[0].text,
                           time=self.get_time,
                           filePicture=self.request.data.message[0].file_picture,
                           fileVideo=self.request.data.message[0].file_video,
                           fileAudio=self.request.data.message[0].file_audio,
                           fileDocument=self.request.data.message[0].file_audio,
                           emoji=self.request.data.message[0].emoji,
                           editedTime=self.request.data.message[0].edited_time,
                           editedStatus=self.request.data.
                           message[0].edited_status,
                           userConfig=self.request.data.user[0].uuid,
                           flow=self.request.data.flow[0].id)
            self.__catching_error(200)

    def _add_flow(self):
        """Function allows you to add a new flow to the database

        """
        # FIXME после замены flowId на UUID из питоньего модуля
        random.seed(urandom(64))
        flow_id = random.randrange(1, 999999)
        if self.request.data.flow[0].type not in ["chat", "group", "channel"]:
            self.__catching_error(400, "Wrong flow type")
        elif self.request.data.flow[0].type == 'chat' and len(self.request.data.user) < 2:
            self.__catching_error(400, "Two users UUID must be specified for chat")
        else:
            try:
                models.Flow(flowId=flow_id,
                            timeCreated=self.get_time,
                            flowType=self.request.data.flow[0].type,
                            title=self.request.data.flow[0].title,
                            info=self.request.data.flow[0].info)
            except SQLObjectIntegrityError as flow_error:
                self.__catching_error(520, str(flow_error))
            else:
                flow = api.Flow()
                flow.id = flow_id
                flow.time = self.get_time
                flow.type = self.request.data.flow[0].type
                flow.title = self.request.data.flow[0].title
                flow.info = self.request.data.flow[0].info
                self.response.data.flow.append(flow)
                self.__catching_error(200)

    def _all_flow(self):
        """Function allows to get a list of all flows and
        information about them from the database

        """
        dbquery = models.Flow.select(models.Flow.q.flowId >= 1)
        if dbquery.count():
            for element in dbquery:
                flow = api.Flow()
                flow.id = element.flowId
                flow.time = element.timeCreated
                flow.type = element.flowType
                flow.title = element.title
                flow.info = element.info
                self.response.data.flow.append(flow)
            self.__catching_error(200)
        else:
            self.__catching_error(404)

    def _user_info(self):
        """Provides information about all personal settings of user.

        """
        try:
            dbquery = models.UserConfig.selectBy(uuid=self.request.data.user[0].uuid).getOne()
        except (SQLObjectIntegrityError, SQLObjectNotFound) as user_info_error:
            self.__catching_error(404, str(user_info_error))
        else:
            user = api.User()
            user.uuid = dbquery.uuid
            user.login = dbquery.login
            user.username = dbquery.username
            user.is_bot = dbquery.isBot
            user.email = dbquery.email
            user.avatar = dbquery.avatar
            user.bio = dbquery.bio
            self.response.data.user.append(user)
            self.__catching_error(200)

    def _authentification(self):
        """Performs authentification of registered client,
        with issuance of a unique hash number of connection session.
        During authentification password transmitted by client
        and password contained in server database are verified.

        """
        if self.__check_login(self.request.data.user[0].login) is False:
            self.__catching_error(404)
        else:
            dbquery = models.UserConfig.selectBy(login=self.request.data.user[0].login).getOne()
            generator = lib.Hash(password=self.request.data.user[0].password,
                                 uuid=dbquery.uuid,
                                 salt=dbquery.salt,
                                 key=dbquery.key,
                                 hash_password=dbquery.hashPassword)
            if generator.check_password():
                dbquery.authId = generator.auth_id()
                user = api.User()
                user.uuid = dbquery.uuid
                user.auth_id = dbquery.authId
                self.response.data.user.append(user)
                self.__catching_error(200)
            else:
                self.__catching_error(401)

    def _delete_user(self):
        """Function irretrievably deletes the user from the database.

        """
        try:
            dbquery = models.UserConfig.selectBy(login=self.request.data.user[0].login,
                                                 password=self.request.data.user[0].password).getOne()
        except (SQLObjectIntegrityError, SQLObjectNotFound) as not_found:
            self.__catching_error(404, str(not_found))
        else:
            dbquery.delete(dbquery.id)
            self.__catching_error(200)

    def _delete_message(self):
        """Function deletes the message from the database Message table by its ID.

        """
        try:
            dbquery = models.Message.selectBy(id=self.request.data.message[0].id).getOne()
        except (SQLObjectIntegrityError, SQLObjectNotFound) as not_found:
            self.__catching_error(404, str(not_found))
        else:
            dbquery.delete(dbquery.id)
            self.__catching_error(200)

    def _edited_message(self):
        """Function changes the text and time in the database Message table.
        The value of the editedStatus column changes from None to True.

        """
        try:
            dbquery = models.Message.selectBy(id=self.request.data.message[0].id).getOne()
        except (SQLObjectIntegrityError, SQLObjectNotFound) as not_found:
            self.__catching_error(404, str(not_found))
        else:
            # changing in DB text, time and status
            dbquery.text = self.request.data.message[0].text
            dbquery.editedTime = self.get_time
            dbquery.editedStatus = True
            self.__catching_error(200)

    def _all_messages(self):
        """Function displays all messages of a specific flow retrieves them
        from the database and issues them as an array consisting of JSON

        """
        dbquery = models.Message.select(
            AND(models.Message.q.flowID == self.request.data.flow[0].id,
                models.Message.q.time >= self.request.data.time))
        if dbquery.count():
            for element in dbquery:
                message = api.Message()
                message.id = element.id
                message.from_flow_id = element.flowID
                message.from_user_uuid = element.userConfigID
                message.text = element.text
                message.time = element.time
                message.file_picture = element.filePicture
                message.file_video = element.fileVideo
                message.file_audio = element.fileAudio
                message.file_document = element.fileDocument
                message.emoji = element.emoji
                message.edited_time = element.editedTime
                message.edited_status = element.editedStatus
                self.response.data.message.append(message)
            self.__catching_error(200)
        else:
            self.__catching_error(404)

    def _ping_pong(self):
        """The function generates a response to a client's request
        for communication between the server and the client.

        """
        self.__catching_error(200)

    def _errors(self):
        """Function handles cases when a request to server is not recognized by it.
        You get a standard answer type: error, which contains an object
        with a description of the error.

        """
        self.__catching_error(405)
