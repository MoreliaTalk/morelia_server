from time import time
from typing import Union
from uuid import uuid4

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
    """Processing requests and forming answers according to "Udav" protocol.
    Protocol version and it's actual description:
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
        """Generates a JSON-object containing result
        of an instance of ProtocolMethod class.

        """
        return self.response.toJSON()

    def __check_auth_token(self, uuid: Union[str, int],
                           auth_id: str) -> bool:
        """Checks uuid and auth_id of user

        Args:
            uuid (int, requires): Unique User ID
            auth_id (str, requires): authentification ID

        Returns:
            True if successful
            False if unsuccessful
        """
        if isinstance(uuid, int):
            uuid = str(uuid)
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
        """Checks database for a user with the same login

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
                         add_info: Union[Exception, str] = None) -> None:
        """Сatches errors in "try...except" content.
        Result is 'dict' with information about code, status,
        time and detailed description of error that has occurred.
        For errors like Exception and other unrecognized errors,
        code "520" and status "Unknown Error" are used.
        FIXME Добавить автоматическую запись информации в лог.

        Args:
            code (Union[int, str]): Error code or type and exception
            description.
            add_info (Optional[str], optional): Additional information
            to be added. 'Exception' field is not used for exceptions.
            Defaults to None.

        Returns:
            dict: returns 'dict' according to  protocol,
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
        """Registers user who is not in the database.
        Note: This version also authentificate user, that exist in database

        """
        uuid = str(uuid4().int)
        password = self.request.data.user[0].password
        login = self.request.data.user[0].login
        username = self.request.data.user[0].username
        email = self.request.data.user[0].email
        if self.__check_login(login):
            self.__catching_error(409)
        else:
            generated = lib.Hash(password=password,
                                 uuid=uuid)
            auth_id = generated.auth_id()
            models.UserConfig(uuid=uuid,
                              password=password,
                              hashPassword=generated.password_hash(),
                              login=login,
                              username=username,
                              email=email,
                              key=generated.get_key(),
                              salt=generated.get_salt(),
                              authId=auth_id)
            user = api.User()
            user.uuid = uuid
            user.auth_id = auth_id
            self.response.data.user.append(user)
            self.__catching_error(201)

    def _get_update(self):
        """Provides updates of flows, messages and users in them from time "time"

        """
        # select all fields of the user table
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
                message.uuid = element.uuid
                message.text = element.text
                message.from_user = element.user.uuid
                message.time = element.time
                message.from_flow = element.flow.uuid
                message.file_picture = element.filePicture
                message.file_video = element.fileVideo
                message.file_audio = element.fileAudio
                message.file_document = element.fileDocument
                message.emoji = element.emoji
                message.edited_time = element.editedTime
                message.edited_status = element.editedStatus
                self.response.data.message.append(message)
        else:
            self.response.data.message

        if dbquery_flow.count():
            for element in dbquery_flow:
                flow = api.Flow()
                flow.uuid = element.uuid
                flow.time = element.timeCreated
                flow.type = element.flowType
                flow.title = element.title
                flow.info = element.info
                flow.owner = element.owner
                flow.users = [item.uuid for item in element.users]
                self.response.data.flow.append(flow)
        else:
            self.response.data.flow

        if dbquery_user.count():
            for element in dbquery_user:
                user = api.User()
                user.uuid = element.uuid
                user.username = element.username
                user.is_bot = element.isBot
                user.avatar = element.avatar
                user.bio = element.bio
                self.response.data.user.append(user)
        else:
            self.response.data.user
        self.__catching_error(200)

    def _send_message(self):
        """Saves user message in database.

        """
        message_uuid = str(uuid4().int)
        flow_uuid = self.request.data.flow[0].uuid
        text = self.request.data.message[0].text
        picture = self.request.data.message[0].file_picture
        video = self.request.data.message[0].file_video
        audio = self.request.data.message[0].file_audio
        document = self.request.data.message[0].file_document
        emoji = self.request.data.message[0].emoji
        user_uuid = self.request.data.user[0].uuid
        try:
            flow = models.Flow.selectBy(uuid=flow_uuid).getOne()
            user = models.UserConfig.selectBy(uuid=user_uuid).getOne()
        except SQLObjectNotFound as flow_error:
            self.__catching_error(404, str(flow_error))
        else:
            models.Message(uuid=message_uuid,
                           text=text,
                           time=self.get_time,
                           filePicture=picture,
                           fileVideo=video,
                           fileAudio=audio,
                           fileDocument=document,
                           emoji=emoji,
                           editedTime=None,
                           editedStatus=False,
                           user=user,
                           flow=flow)
            message = api.Message()
            message.from_flow = flow_uuid
            message.from_user = user_uuid
            message.uuid = message_uuid
            self.response.data.message.append(message)
            self.__catching_error(200)

    def _all_messages(self):
        """Displays all messages of a specific flow retrieves them
        from database and issues them as an array consisting of JSON

        """
        flow = api.Flow()
        flow_uuid = self.request.data.flow[0].uuid
        message_start = self.request.data.flow[0].message_start
        message_end = self.request.data.flow[0].message_end
        if message_start is None:
            message_start = 0
        if message_end is None:
            message_end = 0
        message_volume = message_end - message_start

        def get_messages(db, end: int, start: int = 0) -> None:
            for element in db[start:end]:
                message = api.Message()
                message.from_flow = element.flow.uuid
                message.from_user = element.user.uuid
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

        try:
            flow_dbquery = models.Flow.selectBy(uuid=flow_uuid).getOne()
            dbquery = models.Message.select(
                AND(models.Message.q.flow == flow_dbquery,
                    models.Message.q.time >= self.request.data.time))
            MESSAGE_COUNT: int = dbquery.count()
            dbquery[0]
        except SQLObjectIntegrityError as flow_error:
            self.__catching_error(520, str(flow_error))
        except (IndexError, SQLObjectNotFound) as flow_error:
            self.__catching_error(404, str(flow_error))
        else:
            if MESSAGE_COUNT <= config.LIMIT_MESSAGE:
                self.response.data.flow.append(flow)
                get_messages(dbquery, config.LIMIT_MESSAGE)
                self.__catching_error(200)
            elif MESSAGE_COUNT > config.LIMIT_MESSAGE:
                flow.message_end = MESSAGE_COUNT
                self.response.data.flow.append(flow)
                if message_volume <= config.LIMIT_MESSAGE:
                    get_messages(dbquery,
                                 self.request.data.flow[0].message_end,
                                 self.request.data.flow[0].message_start)
                    self.__catching_error(206)
                else:
                    self.__catching_error(403, "Requested more messages"
                                          f" than server limit"
                                          f" (<{config.LIMIT_MESSAGE})")

    def _add_flow(self):
        """Allows add a new flow to database

        """
        flow_uuid = str(uuid4().hex)
        owner = self.request.data.flow[0].owner
        users = self.request.data.flow[0].users
        flow_type = self.request.data.flow[0].type
        if flow_type not in ["chat", "group", "channel"]:
            error = "Wrong flow type"
            self.__catching_error(400, error)
        elif flow_type == 'chat' and len(users) != 2:
            error = "Two users UUID must be specified for chat"
            self.__catching_error(400, error)
        else:
            try:
                dbquery = models.Flow(uuid=flow_uuid,
                                      timeCreated=self.get_time,
                                      flowType=flow_type,
                                      title=self.request.data.flow[0].title,
                                      info=self.request.data.flow[0].info,
                                      owner=owner)
                for user_uuid in users:
                    user = models.UserConfig.selectBy(uuid=user_uuid).getOne()
                    dbquery.addUserConfig(user)
            except SQLObjectIntegrityError as flow_error:
                self.__catching_error(520, str(flow_error))
            else:
                flow = api.Flow()
                flow.uuid = flow_uuid
                flow.time = self.get_time
                flow.type = self.request.data.flow[0].type
                flow.title = self.request.data.flow[0].title
                flow.info = self.request.data.flow[0].info
                flow.owner = owner
                flow.users = users
                self.response.data.flow.append(flow)
                self.__catching_error(200)

    def _all_flow(self):
        """Allows to get a list of all flows and information about them
        from database

        """
        dbquery = models.Flow.selectBy()
        if dbquery.count():
            for element in dbquery:
                flow = api.Flow()
                flow.uuid = element.uuid
                flow.time = element.timeCreated
                flow.type = element.flowType
                flow.title = element.title
                flow.info = element.info
                flow.owner = element.owner
                flow.users = [item.uuid for item in element.users]
                self.response.data.flow.append(flow)
            self.__catching_error(200)
        else:
            self.__catching_error(404)

    def _user_info(self):
        """Provides information about all personal settings of user.

        """
        users_volume = len(self.request.data.user)
        if users_volume <= config.LIMIT_USERS:
            for element in self.request.data.user[1:]:
                try:
                    dbquery = models.UserConfig.selectBy(uuid=element.uuid).getOne()
                except SQLObjectIntegrityError as user_info_error:
                    self.__catching_error(520, str(user_info_error))
                else:
                    user = api.User()
                    user.uuid = dbquery.uuid
                    user.login = dbquery.login
                    user.username = dbquery.username
                    user.is_bot = dbquery.isBot
                    user.avatar = dbquery.avatar
                    user.bio = dbquery.bio
                    self.response.data.user.append(user)
            self.__catching_error(200)
        else:
            self.__catching_error(403, f"Requested more {config.LIMIT_USERS}"
                                  " users than server limit")

    def _authentification(self):
        """Performs authentification of registered client,
        with issuance of a unique hash number of connection session.
        During authentification password transmitted by client
        and password contained in server database are verified.

        """
        login = self.request.data.user[0].login
        password = self.request.data.user[0].password
        if self.__check_login(login) is False:
            self.__catching_error(404)
        else:
            dbquery = models.UserConfig.selectBy(login=login).getOne()
            # to check password, we use same module as for its
            # hash generation. Specify password entered by user
            # and hash of old password as parameters.
            # After that, hashes are compared using "check_password" method.
            generator = lib.Hash(password=password,
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
        """Function irretrievably deletes the user from database.

        """
        uuid = str(uuid4().int)
        login = self.request.data.user[0].login
        password = self.request.data.user[0].password
        try:
            dbquery = models.UserConfig.selectBy(login=login,
                                                 password=password).getOne()
        except (SQLObjectIntegrityError, SQLObjectNotFound) as not_found:
            self.__catching_error(404, str(not_found))
        else:
            dbquery.login = "User deleted"
            dbquery.password = uuid
            dbquery.hashPassword = uuid
            dbquery.username = "User deleted"
            dbquery.authId = uuid
            dbquery.email = ""
            dbquery.avatar = b""
            dbquery.bio = "deleted"
            dbquery.salt = b"deleted"
            dbquery.key = b"deleted"
            self.__catching_error(200)

    def _delete_message(self):
        """Function deletes the message from database Message
        table by its ID.

        """
        uuid = self.request.data.message[0].uuid
        try:
            dbquery = models.Message.selectBy(uuid=uuid).getOne()
        except (SQLObjectIntegrityError, SQLObjectNotFound) as not_found:
            self.__catching_error(404, str(not_found))
        else:
            dbquery.text = "Message deleted"
            dbquery.filePicture = b''
            dbquery.fileVideo = b''
            dbquery.fileAudio = b''
            dbquery.fileDocument = b''
            dbquery.emoji = b''
            dbquery.editedTime = self.get_time
            dbquery.editedStatus = True
            self.__catching_error(200)

    def _edited_message(self):
        """Changes text and time in database Message table.
        Value of editedStatus column changes from None to True.

        """
        uuid = self.request.data.message[0].uuid
        try:
            dbquery = models.Message.selectBy(uuid=uuid).getOne()
        except (SQLObjectIntegrityError, SQLObjectNotFound) as not_found:
            self.__catching_error(404, str(not_found))
        else:
            # changing in DB text, time and status
            dbquery.text = self.request.data.message[0].text
            dbquery.editedTime = self.get_time
            dbquery.editedStatus = True
            self.__catching_error(200)

    def _ping_pong(self):
        """Generates a response to a client's request
        for communication between server and client.

        """
        self.__catching_error(200)

    def _errors(self):
        """Handles cases when a request to server is not recognized by it.
        Get a standard answer type: error, which contains an object
        with a description of error.

        """
        self.__catching_error(405)
