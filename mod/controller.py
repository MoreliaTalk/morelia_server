"""
    Copyright (c) 2020 - present NekrodNIK, Stepan Skriabin, rus-ai and other.
    Look at the file AUTHORS.md(located at the root of the project) to get the
    full list.

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

import json
from time import time
from uuid import uuid4
import configparser

from pydantic import ValidationError
from loguru import logger

from mod import api
from mod import error
from mod import lib
from mod.db.dbhandler import DBHandler
from mod.db.dbhandler import DatabaseWriteError
from mod.db.dbhandler import DatabaseReadError
from mod.db.dbhandler import DatabaseAccessError

# ************** Read "config.ini" ********************
config = configparser.ConfigParser()
config.read('config.ini')
limit = config['SERVER_LIMIT']
database = config['DATABASE']
# ************** END **********************************


class Error:
    def __init__(self):
        self.get_time = int(time())

    def catching_error(self, status: str,
                       add_info: Exception | str = None) -> api.ErrorsResponse:
        """Сatches errors in "try...except" content.
        Result is class 'api.ErrorsResponse' with information about code,
        status, time and detailed description of error that has occurred.
        For errors like Exception and other unrecognized errors,
        code "520" and status "Unknown Error" are used.

        Args:
            status (str): Error type
            add_info ([Exception] or [str], optional): Additional information
            to be added. Defaults to None.

        Returns:
            dict: returns class 'api.ErrorsResponse' according to protocol,
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
            code = 520
            status = "Unknown Error"
            time = self.get_time
            detail = str(ERROR)
        else:
            logger.debug(f"Status code({catch_error.code.value}):",
                         f" {catch_error.status.value}")
            code = catch_error.code.value
            status = catch_error.status.value
            time = self.get_time
            if add_info is None:
                detail = catch_error.detail.value
            else:
                detail = add_info

        return api.ErrorsResponse(code,
                                  status,
                                  time,
                                  detail)


class User:
    def __init__(self) -> None:
        self._db = DBHandler()

    def check_auth(method_to_decorate):
        db = DBHandler()
        error = Error()

        def wrapper(*args):
            uuid = args[0].data.user[0].uuid
            auth_id = args[0].data.user[0].auth_id

            try:
                dbquery = db.get_user_by_uuid(uuid)
                logger.success("User was found in the database")
            except DatabaseReadError:
                logger.debug("User wasn't found in the database")
                return error.catching_error("UNAUTHORIZED")
            else:
                if auth_id == dbquery.authId:
                    logger.success("Authentication User has been verified")
                    return method_to_decorate(*args)
                else:
                    logger.debug("Authentication User failed")
                    return error.catching_error("UNAUTHORIZED")

        return wrapper

    def check_login(self,
                    login: str) -> bool:
        """Checks database for a user with the same login

        Args:
            login (str): user login

        Returns:
            True if there is such a user
            False if no such user exists
        """
        try:
            self._db.get_user_by_login(login)
        except (DatabaseReadError, DatabaseAccessError):
            logger.debug("There is no user in the database")
            return False
        else:
            logger.success("User was found in the database")
            return True


class ProtocolMethods(User, Error):
    """Processing requests and forming answers according to "MTP" protocol.
    Protocol version and it's actual description:
    https://github.com/MoreliaTalk/morelia_protocol/blob/master/README.md
    """
    def __init__(self, request):
        self.jsonapi = api.VersionResponse(version=api.VERSION)
        self.get_time: int = int(time())
        self.response = None
        self.request = None
        self._db = DBHandler()
        self._db.connect(uri=database.get('uri'))
        self._db.create()

        try:
            self.request = api.Request.parse_obj(request)
            logger.success("Validation was successful")
        except ValidationError as ERROR:
            self.response = self._errors("UNSUPPORTED_MEDIA_TYPE",
                                         str(ERROR))
            logger.debug(f"Validation failed: {ERROR}")
        else:
            match self.request.type:
                case 'register_user':
                    self.response = self._register_user(self.request)
                case 'auth':
                    self.response = self._authentification(self.request)
                case 'send_message':
                    self.response = self._send_message(self.request)
                case 'all_flow':
                    self.response = self._all_flow(self.request)
                case 'add_flow':
                    self.response = self._add_flow(self.request)
                case 'all_messages':
                    self.response = self._all_messages(self.request)
                case 'delete_user':
                    self.response = self._delete_user(self.request)
                case 'delete_message':
                    self.response = self._delete_message(self.request)
                case 'edited_message':
                    self.response = self._edited_message(self.request)
                case 'get_update':
                    self.response = self._get_update(self.request)
                case 'ping-pong':
                    self.response = self._ping_pong(self.request)
                case 'user_info':
                    self.response = self._user_info(self.request)
                case _:
                    self.response = self._errors()

    def get_response(self,
                     response: api.Response = None) -> json:
        """Generates a JSON-object containing result
        of an instance of ProtocolMethod class.
        """
        if response is None:
            return self.response.json()
        else:
            return response.json()

    def _register_user(self,
                       request: api.Request) -> api.Response:
        """Registers user who is not in the database.
        Note: This version also authentificate user, that exist in database
        """
        uuid = str(uuid4().int)
        password = request.data.user[0].password
        login = request.data.user[0].login
        username = request.data.user[0].username
        email = request.data.user[0].email
        user = []
        data = None

        if self.check_login(login):
            errors = self.catching_error("CONFLICT")
        else:
            generated = lib.Hash(password,
                                 uuid)
            auth_id = generated.auth_id()
            self._db.add_user(uuid,
                              login,
                              password,
                              hash_password=generated.password_hash(),
                              username=username,
                              is_bot=False,
                              auth_id=auth_id,
                              email=email,
                              avatar=None,
                              bio=None,
                              salt=generated.get_salt,
                              key=generated.get_key)
            user.append(api.UserResponse(uuid,
                                         auth_id))
            data = api.DataResponse(self.get_time,
                                    user)
            errors = self.catching_error("CREATED")
            logger.success("User is registred")

        return api.Response(request.type,
                            data,
                            errors,
                            self.jsonapi)

    @User.check_auth
    def _get_update(self,
                    request: api.Request) -> api.Response:
        """Provides updates of flows, messages and users in them from time "time"
        """
        # select all fields of the user table
        # TODO внеести измнения в протокол, добавить фильтр
        # по дате создания пользователя
        message = []
        flow = []
        user = []

        dbquery_user = self._db.get_all_user()
        dbquery_flow = self._db.get_flow_by_more_time(request.data.time)
        dbquery_message = self._db.get_message_by_more_time(request.data.time)

        if dbquery_message.count():
            for element in dbquery_message:
                message.append(api.MessageResponse(
                               element.uuid,
                               None,
                               element.text,
                               element.user.uuid,
                               element.time,
                               element.flow.uuid,
                               element.filePicture,
                               element.fileVideo,
                               element.fileAudio,
                               element.fileDocument,
                               element.emoji,
                               element.editedTime,
                               element.editedStatus))

        if dbquery_flow.count():
            for element in dbquery_flow:
                flow.append(api.FlowResponse(
                            element.uuid,
                            element.timeCreated,
                            element.flowType,
                            element.title,
                            element.info,
                            element.owner,
                            users=[item.uuid for item in element.users]))

        if dbquery_user.count():
            for element in dbquery_user:
                user.append(api.UserResponse(
                            element.uuid,
                            element.username,
                            element.isBot,
                            element.avatar,
                            element.bio))

        errors = self.catching_error("OK")
        data = api.DataResponse(self.get_time,
                                flow,
                                message,
                                user)
        logger.success("\'_get_update\' executed successfully")

        return api.Response(request.type,
                            data,
                            errors,
                            self.jsonapi)

    @User.check_auth
    def _send_message(self,
                      request: api.Request) -> api.Response:
        """Saves user message in database.
        """
        message_uuid = str(uuid4().int)
        flow_uuid = request.data.flow[0].uuid
        text = request.data.message[0].text
        picture = request.data.message[0].file_picture
        video = request.data.message[0].file_video
        audio = request.data.message[0].file_audio
        document = request.data.message[0].file_document
        emoji = request.data.message[0].emoji
        user_uuid = request.data.user[0].uuid
        client_id = request.data.message[0].client_id
        message = []
        data = None

        try:
            self._db.add_message(flow_uuid,
                                 user_uuid,
                                 message_uuid,
                                 self.get_time,
                                 text,
                                 picture,
                                 video,
                                 audio,
                                 document,
                                 emoji)
        except DatabaseWriteError as ERROR:
            errors = self.catching_error("NOT_FOUND",
                                         str(ERROR))
        else:
            message.append(api.MessageResponse(message_uuid,
                                               client_id,
                                               flow_uuid,
                                               user_uuid))
            data = api.DataResponse(self.get_time,
                                    message)
            logger.success("\'_send_message\' executed successfully")
            errors = self.catching_error("OK")

        return api.Response(request.type,
                            data,
                            errors,
                            self.jsonapi)

    @User.check_auth
    def _all_messages(self,
                      request: api.Request) -> api.Response:
        """Displays all messages of a specific flow retrieves them
        from database and issues them as an array consisting of JSON
        """
        flow_uuid = request.data.flow[0].uuid
        flow = []
        message = []

        if request.data.flow[0].message_start is None:
            message_start = 0
        else:
            message_start = request.data.flow[0].message_start

        if request.data.flow[0].message_end is None:
            message_end = 0
        else:
            message_end = request.data.flow[0].message_end

        message_volume = message_end - message_start

        def get_messages(db,
                         end: int,
                         start: int = 0) -> list:
            message = []
            for element in db[start:end]:
                message.append(api.MessageResponse(
                               element.uuid,
                               None,
                               element.flow.uuid,
                               element.user.uuid,
                               element.text,
                               element.time,
                               element.filePicture,
                               element.fileVideo,
                               element.fileAudio,
                               element.fileDocument,
                               element.emoji,
                               element.editedTime,
                               element.editedStatus))
            return message

        try:
            dbquery = self._db.get_message_by_more_time_and_flow(flow_uuid,
                                                                 request.data.time)
            MESSAGE_COUNT: int = dbquery.count()
            dbquery[0]
        except DatabaseReadError as flow_error:
            errors = self.catching_error("NOT_FOUND",
                                         str(flow_error))
        else:
            if MESSAGE_COUNT <= limit.getint("messages"):
                flow.append(api.FlowResponse(flow_uuid,
                                             message_start,
                                             message_end))
                message = get_messages(dbquery,
                                       limit.getint("messages"))
                errors = self.catching_error("OK")
                logger.success("\'_all_messages\' executed successfully")
            else:
                flow.append(api.FlowResponse(flow_uuid,
                                             message_start,
                                             MESSAGE_COUNT))
                if message_volume <= limit.getint("messages"):
                    message = get_messages(dbquery,
                                           request.data.flow[0].message_end,
                                           request.data.flow[0].message_start)
                    logger.success("\'_all_messages\' executed successfully")
                    errors = self.catching_error("PARTIAL_CONTENT")
                else:
                    errors = self.catching_error("FORBIDDEN",
                                                 "Requested more messages"
                                                 f" than server limit"
                                                 f" (<{limit.getint('messages')})")

        data = api.DataResponse(self.get_time,
                                flow,
                                message)

        return api.Response(request.type,
                            data,
                            errors,
                            self.jsonapi)

    @User.check_auth
    def _add_flow(self,
                  request: api.Request) -> api.Response:
        """Allows add a new flow to database
        """
        flow_uuid = str(uuid4().int)
        owner = request.data.flow[0].owner
        users = request.data.flow[0].users
        flow_type = request.data.flow[0].type
        flow = []

        if flow_type not in ["chat",
                             "group",
                             "channel"]:
            errors = self.catching_error("BAD_REQUEST",
                                         "Wrong flow type")
        elif flow_type == 'chat' and len(users) != 2:
            errors = self.catching_error("BAD_REQUEST",
                                         "Must be two users only")
        else:
            try:
                self._db.add_flow(flow_uuid,
                                  self.get_time,
                                  flow_type,
                                  request.data.flow[0].title,
                                  request.data.flow[0].info,
                                  owner)
            except DatabaseWriteError as flow_error:
                errors = self.catching_error("NOT_FOUND",
                                             str(flow_error))
            else:
                flow.append(api.FlowResponse(flow_uuid,
                                             self.get_time,
                                             request.data.flow[0].type,
                                             request.data.flow[0].title,
                                             request.data.flow[0].info,
                                             owner,
                                             users))
                errors = self.catching_error("OK")
                logger.success("\'_add_flow\' executed successfully")

        data = api.DataResponse(self.get_time,
                                flow)

        return api.Response(request.type,
                            data,
                            errors,
                            self.jsonapi)

    @User.check_auth
    def _all_flow(self,
                  request: api.Request) -> api.Response:
        """Allows to get a list of all flows and information about them
        from database
        """
        flow = []
        dbquery = self._db.get_all_flow()

        if dbquery.count():
            for element in dbquery:
                flow.append(api.FlowResponse(
                            element.uuid,
                            element.timeCreated,
                            element.flowType,
                            element.title,
                            element.info,
                            element.owner,
                            users=[item.uuid for item in element.users]))
            errors = self.catching_error("OK")
            logger.success("\'_all_flow\' executed successfully")
        else:
            errors = self.catching_error("NOT_FOUND")

        data = api.DataResponse(self.get_time,
                                flow)

        return api.Response(request.type,
                            data,
                            errors,
                            self.jsonapi)

    @User.check_auth
    def _user_info(self,
                   request: api.Request) -> api.Response:
        """Provides information about all personal settings of user.
        """
        users_volume = len(request.data.user)
        user = []

        if users_volume <= limit.getint("users"):
            for element in request.data.user[1:]:
                try:
                    dbquery = self._db.get_flow_by_uuid(element.uuid)
                except (DatabaseReadError,
                        DatabaseAccessError) as user_info_error:
                    errors = self.catching_error("UNKNOWN_ERROR",
                                                 str(user_info_error))
                else:
                    user.append(api.UserResponse(dbquery.uuid,
                                                 dbquery.login,
                                                 dbquery.username,
                                                 dbquery.isBot,
                                                 dbquery.avatar,
                                                 dbquery.bio))
            errors = self.catching_error("OK")
            logger.success("\'_user_info\' executed successfully")
        else:
            errors = self.catching_error("FORBIDDEN",
                                         f"Requested more {limit.get('users')}"
                                         " users than server limit")

        data = api.DataResponse(self.get_time,
                                user)

        return api.Response(request.type,
                            data,
                            errors,
                            self.jsonapi)

    def _authentification(self,
                          request: api.Request) -> api.Response:
        """Performs authentification of registered client,
        with issuance of a unique hash number of connection session.
        During authentification password transmitted by client
        and password contained in server database are verified.
        """
        login = request.data.user[0].login
        password = request.data.user[0].password
        user = []

        if self.check_login(login):
            dbquery = self._db.get_user_by_login(login)
            # to check password, we use same module as for its
            # hash generation. Specify password entered by user
            # and hash of old password as parameters.
            # After that, hashes are compared using "check_password" method.
            generator = lib.Hash(password,
                                 dbquery.uuid,
                                 dbquery.salt,
                                 dbquery.key,
                                 dbquery.hashPassword)
            if generator.check_password():
                dbquery.authId = generator.auth_id()
                user.append(api.UserResponse(dbquery.uuid,
                                             dbquery.authId))
                errors = self.catching_error("OK")
                logger.success("\'_authentification\' executed successfully")
            else:
                errors = self.catching_error("UNAUTHORIZED")
        else:
            errors = self.catching_error("NOT_FOUND")

        data = api.DataResponse(self.get_time,
                                user)

        return api.Response(request.type,
                            data,
                            errors,
                            self.jsonapi)

    @User.check_auth
    def _delete_user(self,
                     request: api.Request) -> api.Response:
        """Function irretrievably deletes the user from database.
        """
        uuid = str(uuid4().int)
        login = request.data.user[0].login
        password = request.data.user[0].password

        try:
            dbquery = self._db.get_user_by_login_and_password(login,
                                                              password)
        except (DatabaseReadError,
                DatabaseAccessError) as not_found:
            errors = self.catching_error("NOT_FOUND",
                                         str(not_found))
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
            errors = self.catching_error("OK")
            logger.success("\'_delete_user\' executed successfully")

        return api.Response(request.type,
                            None,
                            errors,
                            self.jsonapi)

    @User.check_auth
    def _delete_message(self,
                        request: api.Request) -> api.Response:
        """Function deletes the message from database Message
        table by its ID.
        """
        message_uuid = request.data.message[0].uuid

        try:
            dbquery = self._db.get_message_by_uuid(message_uuid)
        except (DatabaseReadError,
                DatabaseAccessError) as not_found:
            errors = self.catching_error("NOT_FOUND",
                                         str(not_found))
        else:
            dbquery.text = "Message deleted"
            dbquery.filePicture = b''
            dbquery.fileVideo = b''
            dbquery.fileAudio = b''
            dbquery.fileDocument = b''
            dbquery.emoji = b''
            dbquery.editedTime = self.get_time
            dbquery.editedStatus = True
            errors = self.catching_error("OK")
            logger.success("\'_delete_message\' executed successfully")

        return api.Response(request.type,
                            None,
                            errors,
                            self.jsonapi)

    @User.check_auth
    def _edited_message(self,
                        request: api.Request) -> api.Response:
        """Changes text and time in database Message table.
        Value of editedStatus column changes from None to True.
        """
        message_uuid = request.data.message[0].uuid

        try:
            dbquery = self._db.get_message_by_uuid(message_uuid)
        except (DatabaseReadError,
                DatabaseAccessError) as not_found:
            errors = self.catching_error("NOT_FOUND",
                                         str(not_found))
        else:
            dbquery.text = request.data.message[0].text
            dbquery.editedTime = self.get_time
            dbquery.editedStatus = True
            errors = self.catching_error("OK")
            logger.success("\'_edited_message\' executed successfully")

        return api.Response(request.type,
                            None,
                            errors,
                            self.jsonapi)

    @User.check_auth
    def _ping_pong(self,
                   request: api.Request) -> api.Response:
        """Generates a response to a client's request
        for communication between server and client.
        """
        errors = self.catching_error("OK")
        logger.success("\'_ping_pong\' executed successfully")

        return api.Response(request.type,
                            None,
                            errors,
                            self.jsonapi)

    def _errors(self,
                status: str = None,
                add_info: Exception | str = None,
                request: api.Request = None) -> api.Response:
        """Handles cases when a request to server is not recognized by it.
        Get a standard answer type: error, which contains an object
        with a description of error.
        """
        if request is not None:
            response = request.type
        else:
            response = "error"

        if status is None:
            status = "METHOD_NOT_ALLOWED"

        errors = self.catching_error(status, add_info)
        logger.success("\'_errors\' executed successfully")

        return api.Response(response,
                            None,
                            errors,
                            self.jsonapi)
