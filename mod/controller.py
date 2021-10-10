"""
    Copyright (c) 2020 - present NekrodNIK, Stepan Scryabin, rus-ai and other.
    Look at the file AUTHORS.md(located at the root of the project) to get the full list.

    This file is part of Morelia Server.

    Morelia Server is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Morelia Server is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with Morelia Server. If not, see <https://www.gnu.org/licenses/>.
"""

from time import time
from uuid import uuid4
import configparser

from pydantic import ValidationError
from sqlobject import AND
from sqlobject import SQLObjectIntegrityError
from sqlobject import SQLObjectNotFound
from sqlobject import dberrors
from loguru import logger

from mod import api
from mod import error
from mod import lib
from mod import models

# ************** Read "config.ini" ********************
config = configparser.ConfigParser()
config.read('config.ini')
limit = config['SERVER_LIMIT']
# ************** END **********************************


class Error:
    def catching_error(self, status: str,
                       add_info: Exception | str = None) -> None:
        """Сatches errors in "try...except" content.
        Result is 'dict' with information about code, status,
        time and detailed description of error that has occurred.
        For errors like Exception and other unrecognized errors,
        code "520" and status "Unknown Error" are used.

        Args:
            status (str): Error type
            add_info (Union[Exception, str], optional): Additional information
            to be added. Defaults to None.

        Returns:
            dict: returns 'dict' according to protocol,
                like: {
                    'code': 200,
                    'status': 'Ok',
                    'time': 123456545,
                    'detail': 'successfully'
                    }
        """
        try:
            catch_error = error.check_error_pattern(status)
        except Exception as ERROR:
            logger.exception(str(ERROR))
            self.response.errors.code = 520
            self.response.errors.status = 'Unknown Error'
            self.response.errors.time = self.get_time
            self.response.errors.detail = (ERROR,
                                           "Maybe wrong type status error? ",
                                           f"Received {type(status)}, ",
                                           "but expected str")
        else:
            self.response.errors.code = catch_error.code.value
            self.response.errors.status = catch_error.status.value
            self.response.errors.time = self.get_time
            if add_info is None:
                self.response.errors.detail = catch_error.detail.value
            else:
                self.response.errors.detail = add_info
            logger.debug(f"Status code({catch_error.code.value}): ",
                         f"{catch_error.status.value}")


class User(Error):
    def __init__(self):
        pass

    def check_auth(method_to_decorate):
        def wrapper(self, *args):
            uuid, auth_id = args
            try:
                dbquery = models.UserConfig.selectBy(uuid=uuid).getOne()
                logger.success("User was found in the database")
            except (dberrors.OperationalError,
                    SQLObjectIntegrityError,
                    SQLObjectNotFound):
                logger.debug("User wasn't found in the database")
                return self.catching_error("UNAUTHORIZED")
            else:
                if auth_id == dbquery.authId:
                    logger.success("Authentication User has been verified")
                    return method_to_decorate(self, *args)
                else:
                    logger.debug("Authentication User failed")
                    return self.catching_error("UNAUTHORIZED")
        return wrapper


class ProtocolMethods(User, Error):
    """Processing requests and forming answers according to "MTP" protocol.
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
        self.response.jsonapi.version = api.VERSION
        self.get_time = int(time())

        try:
            self.request = api.ValidJSON.parse_obj(request)
            logger.success("Validation was successful")
        except ValidationError as ERROR:
            self.response.type = "errors"
            self.catching_error("UNSUPPORTED_MEDIA_TYPE",
                                str(ERROR))
            logger.debug(f"Validation failed: {ERROR}")
        else:
            self.response.type = self.request.type
            uuid = self.request.data.user[0].uuid
            auth_id = self.request.data.user[0].auth_id
            match self.request.type:
                case 'register_user':
                    self._register_user()
                case 'auth':
                    self._authentification()
                case 'send_message':
                    self._send_message(uuid, auth_id)
                case 'all_flow':
                    self._all_flow(uuid, auth_id)
                case 'add_flow':
                    self._add_flow(uuid, auth_id)
                case 'all_messages':
                    self._all_messages(uuid, auth_id)
                case 'delete_user':
                    self._delete_user(uuid, auth_id)
                case 'delete_message':
                    self._delete_message(uuid, auth_id)
                case 'edited_message':
                    self._edited_message(uuid, auth_id)
                case 'get_update':
                    self._get_update(uuid, auth_id)
                case 'ping-pong':
                    self._ping_pong(uuid, auth_id)
                case 'user_info':
                    self._user_info(uuid, auth_id)
                case _:
                    self._errors()

    def get_response(self):
        """Generates a JSON-object containing result
        of an instance of ProtocolMethod class.
        """
        return self.response.toJSON()

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
            logger.debug("There is no user in the database")
            return False
        else:
            logger.success("User was found in the database")
            return True

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
            self.catching_error("CONFLICT")
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
            logger.success("User is registred")
            self.catching_error("CREATED")

    @User.check_auth
    def _get_update(self, *args):
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
        logger.success("\'_get_update\' executed successfully")
        self.catching_error("OK")

    @User.check_auth
    def _send_message(self, *args):
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
        user_uuid, _ = args
        try:
            flow = models.Flow.selectBy(uuid=flow_uuid).getOne()
            user = models.UserConfig.selectBy(uuid=user_uuid).getOne()
        except SQLObjectNotFound as ERROR:
            self.catching_error("NOT_FOUND", str(ERROR))
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
            message.client_id = self.request.data.message[0].client_id
            message.from_flow = flow_uuid
            message.from_user = user_uuid
            message.uuid = message_uuid
            self.response.data.message.append(message)
            logger.success("\'_send_message\' executed successfully")
            self.catching_error("OK")

    @User.check_auth
    def _all_messages(self, *args):
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
                message.uuid = element.uuid
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
            self.catching_error("UNKNOWN_ERROR", str(flow_error))
        except (IndexError, SQLObjectNotFound) as flow_error:
            self.catching_error("NOT_FOUND", str(flow_error))
        else:
            if MESSAGE_COUNT <= limit.getint("messages"):
                self.response.data.flow.append(flow)
                get_messages(dbquery, limit.getint("messages"))
                logger.success("\'_all_messages\' executed successfully")
                self.catching_error("OK")
            elif MESSAGE_COUNT > limit.getint("messages"):
                flow.message_end = MESSAGE_COUNT
                self.response.data.flow.append(flow)
                if message_volume <= limit.getint("messages"):
                    get_messages(dbquery,
                                 self.request.data.flow[0].message_end,
                                 self.request.data.flow[0].message_start)
                    logger.success("\'_all_messages\' executed successfully")
                    self.catching_error("PARTIAL_CONTENT")
                else:
                    self.catching_error("FORBIDDEN",
                                        "Requested more messages"
                                        f" than server limit"
                                        f" (<{limit.getint('messages')})")

    @User.check_auth
    def _add_flow(self, *args):
        """Allows add a new flow to database
        """
        flow_uuid = str(uuid4().hex)
        owner = self.request.data.flow[0].owner
        users = self.request.data.flow[0].users
        flow_type = self.request.data.flow[0].type
        if flow_type not in ["chat", "group", "channel"]:
            self.catching_error("BAD_REQUEST", "Wrong flow type")
        elif flow_type == 'chat' and len(users) != 2:
            self.catching_error("BAD_REQUEST", "Must be two users only")
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
                self.catching_error("UNKNOWN_ERROR", str(flow_error))
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
                logger.success("\'_add_flow\' executed successfully")
                self.catching_error("OK")

    @User.check_auth
    def _all_flow(self, *args):
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
            logger.success("\'_all_flow\' executed successfully")
            self.catching_error("OK")
        else:
            self.catching_error("NOT_FOUND")

    @User.check_auth
    def _user_info(self, *args):
        """Provides information about all personal settings of user.
        """
        users_volume = len(self.request.data.user)
        if users_volume <= limit.getint("users"):
            for element in self.request.data.user[1:]:
                try:
                    dbquery = models.UserConfig.selectBy(uuid=element.uuid).getOne()
                except SQLObjectIntegrityError as user_info_error:
                    self.catching_error("UNKNOWN_ERROR",
                                        str(user_info_error))
                else:
                    user = api.User()
                    user.uuid = dbquery.uuid
                    user.login = dbquery.login
                    user.username = dbquery.username
                    user.is_bot = dbquery.isBot
                    user.avatar = dbquery.avatar
                    user.bio = dbquery.bio
                    self.response.data.user.append(user)
            logger.success("\'_user_info\' executed successfully")
            self.catching_error("OK")
        else:
            self.catching_error("FORBIDDEN",
                                f"Requested more {limit.get('users')}"
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
            self.catching_error("NOT_FOUND")
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
                logger.success("\'_authentification\' executed successfully")
                self.catching_error("OK")
            else:
                self.catching_error("UNAUTHORIZED")

    @User.check_auth
    def _delete_user(self, *args):
        """Function irretrievably deletes the user from database.
        """
        uuid = str(uuid4().int)
        login = self.request.data.user[0].login
        password = self.request.data.user[0].password
        try:
            dbquery = models.UserConfig.selectBy(login=login,
                                                 password=password).getOne()
        except (SQLObjectIntegrityError, SQLObjectNotFound) as not_found:
            self.catching_error("NOT_FOUND", str(not_found))
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
            logger.success("\'_delete_user\' executed successfully")
            self.catching_error("OK")

    @User.check_auth
    def _delete_message(self, *args):
        """Function deletes the message from database Message
        table by its ID.
        """
        message_uuid = self.request.data.message[0].uuid
        try:
            dbquery = models.Message.selectBy(uuid=message_uuid).getOne()
        except (SQLObjectIntegrityError, SQLObjectNotFound) as not_found:
            self.catching_error("NOT_FOUND", str(not_found))
        else:
            dbquery.text = "Message deleted"
            dbquery.filePicture = b''
            dbquery.fileVideo = b''
            dbquery.fileAudio = b''
            dbquery.fileDocument = b''
            dbquery.emoji = b''
            dbquery.editedTime = self.get_time
            dbquery.editedStatus = True
            logger.success("\'_delete_message\' executed successfully")
            self.catching_error("OK")

    @User.check_auth
    def _edited_message(self, *args):
        """Changes text and time in database Message table.
        Value of editedStatus column changes from None to True.
        """
        message_uuid = self.request.data.message[0].uuid
        try:
            dbquery = models.Message.selectBy(uuid=message_uuid).getOne()
        except (SQLObjectIntegrityError, SQLObjectNotFound) as not_found:
            self.catching_error("NOT_FOUND", str(not_found))
        else:
            # changing in DB text, time and status
            dbquery.text = self.request.data.message[0].text
            dbquery.editedTime = self.get_time
            dbquery.editedStatus = True
            logger.success("\'_edited_message\' executed successfully")
            self.catching_error("OK")

    @User.check_auth
    def _ping_pong(self, *args):
        """Generates a response to a client's request
        for communication between server and client.
        """
        logger.success("\'_ping_pong\' executed successfully")
        self.catching_error("OK")

    def _errors(self):
        """Handles cases when a request to server is not recognized by it.
        Get a standard answer type: error, which contains an object
        with a description of error.
        """
        logger.success("\'_errors\' executed successfully")
        self.catching_error("METHOD_NOT_ALLOWED")
