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
from os import name
from time import time
from typing import Tuple, Type
from uuid import uuid4
import configparser
from collections import namedtuple

from pydantic import ValidationError
from loguru import logger

from mod import api
from mod import error
from mod import lib
from mod.db.dbhandler import DatabaseWriteError
from mod.db.dbhandler import DatabaseReadError
from mod.db.dbhandler import DatabaseAccessError

# ************** Read "config.ini" ********************
config = configparser.ConfigParser()
config.read('config.ini')
limit = config['SERVER_LIMIT']
# ************** END **********************************


class ErrorResponse:
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
        ErrorResponse.result() returns class 'api.ErrorsResponse'
        according to protocol, like:
            {
                'code': 200,
                'status': 'Ok',
                'time': 123456545,
                'detail': 'successfully'
                }
        """

    def __init__(self,
                 status: str,
                 add_info: Exception | str = None) -> None:
        self.status = status
        self.detail = add_info

    def result(self) -> api.ErrorsResponse:
        try:
            catch_error = error.check_error_pattern(self.status)
        except Exception as ERROR:
            logger.exception(str(ERROR))
            code = 520
            status = "Unknown Error"
            time_ = int(time())
            detail = str(ERROR)
        else:
            logger.debug(f"Status code({catch_error.code.value}):",
                         f" {catch_error.status.value}")
            code = catch_error.code.value
            status = catch_error.status.value
            time_ = int(time())
            if self.detail is None:
                detail = catch_error.detail.value
            else:
                detail = self.detail

        return api.ErrorsResponse(code=code,
                                  status=status,
                                  time=time_,
                                  detail=detail)


class ProtocolMethods():
    """Processing requests and forming answers according to "MTP" protocol.
    Protocol version and it's actual description:
    https://github.com/MoreliaTalk/morelia_protocol/blob/master/README.md
    """
    def __init__(self, request, database):
        self.jsonapi = api.VersionResponse(version=api.VERSION)
        self.get_time = int(time())
        self._db = database

        try:
            self.request = api.Request.parse_obj(request)
            logger.success("Validation was successful")
        except ValidationError as ERROR:
            self.response = self._errors("UNSUPPORTED_MEDIA_TYPE",
                                         str(ERROR))
            logger.debug(f"Validation failed: {ERROR}")
        else:
            self.method = getattr(self, f"_{self.request.type}")
            auth = self._check_auth(self.request.data.user[0].uuid,
                                    self.request.data.user[0].auth_id)
            if auth.result:
                self.response = self.method(self.request)
            elif auth.result is not True and self.request.type == 'register_user':
                self.response = self.method(self.request)
            else:
                self.response = self._errors("UNAUTHORIZED",
                                             auth.error_message)

    def _check_auth(self,
                    uuid: str,
                    auth_id: str) -> Type[Tuple]:
        Result = namedtuple('Result', ['result',
                                       'error_message'])
        try:
            dbquery = self._db.get_user_by_uuid(uuid)
            logger.success("User was found in the database")
        except DatabaseReadError:
            message = "User wasn't found in the database"
            logger.debug(message)
            return Result(False,
                          message)
        else:
            if auth_id == dbquery.authId:
                message = "Authentication User has been verified"
                logger.success(message)
                return Result(True,
                              message)
            else:
                message = "Authentication User failed"
                logger.debug(message)
                return Result(False,
                              message)

    def get_response(self,
                     response: api.Response = None) -> json:
        """Generates a JSON-object containing result
        of an instance of ProtocolMethod class.
        """
        if response is None:
            return self.response.json()
        else:
            return response.json()

    def _check_login(self,
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
        except DatabaseReadError:
            logger.debug("There is no user in the database")
            return False
        else:
            logger.success("User was found in the database")
            return True

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

        if self._check_login(login):
            errors = ErrorResponse("CONFLICT")
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
            user.append(api.UserResponse(uuid=uuid,
                                         auth_id=auth_id))
            data = api.DataResponse(time=self.get_time,
                                    user=user)
            errors = ErrorResponse("CREATED")
            logger.success("User is registred")

        return api.Response(type=request.type,
                            data=data,
                            errors=errors.result(),
                            jsonapi=self.jsonapi)

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
                               uuid=element.uuid,
                               client_id=None,
                               text=element.text,
                               from_user=element.user.uuid,
                               time=element.time,
                               from_flow=element.flow.uuid,
                               file_picture=element.filePicture,
                               file_video=element.fileVideo,
                               file_audio=element.fileAudio,
                               file_document=element.fileDocument,
                               emoji=element.emoji,
                               edited_time=element.editedTime,
                               edited_status=element.editedStatus))

        if dbquery_flow.count():
            for element in dbquery_flow:
                flow.append(api.FlowResponse(
                            uuid=element.uuid,
                            time=element.timeCreated,
                            type=element.flowType,
                            title=element.title,
                            info=element.info,
                            owner=element.owner,
                            users=[item.uuid for item in element.users]))

        if dbquery_user.count():
            for element in dbquery_user:
                user.append(api.UserResponse(
                            uuid=element.uuid,
                            username=element.username,
                            is_bot=element.isBot,
                            avatar=element.avatar,
                            bio=element.bio))

        errors = ErrorResponse("OK")
        data = api.DataResponse(time=self.get_time,
                                flow=flow,
                                message=message,
                                user=user)
        logger.success("\'_get_update\' executed successfully")

        return api.Response(type=request.type,
                            date=data,
                            errors=errors.result(),
                            jsonapi=self.jsonapi)

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
            errors = ErrorResponse("NOT_FOUND",
                                   str(ERROR))
        else:
            message.append(api.MessageResponse(uuid=message_uuid,
                                               client_id=client_id,
                                               from_user=user_uuid,
                                               from_flow=flow_uuid))
            data = api.DataResponse(time=self.get_time,
                                    message=message)
            logger.success("\'_send_message\' executed successfully")
            errors = ErrorResponse("OK")

        return api.Response(type=request.type,
                            data=data,
                            errors=errors.result(),
                            jsonapi=self.jsonapi)

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
                               uuid=element.uuid,
                               client_id=None,
                               text=element.text,
                               from_user=element.user.uuid,
                               time=element.time,
                               from_flow=element.flow.uuid,
                               file_picture=element.filePicture,
                               file_video=element.fileVideo,
                               file_audio=element.fileAudio,
                               file_document=element.fileDocument,
                               emoji=element.emoji,
                               edited_time=element.editedTime,
                               edited_status=element.editedStatus))
            return message

        try:
            dbquery = self._db.get_message_by_more_time_and_flow(flow_uuid,
                                                                 request.data.time)
            MESSAGE_COUNT: int = dbquery.count()
            dbquery[0]
        except DatabaseReadError as flow_error:
            errors = ErrorResponse("NOT_FOUND",
                                   str(flow_error))
        else:
            if MESSAGE_COUNT <= limit.getint("messages"):
                flow.append(api.FlowResponse(uuid=flow_uuid,
                                             message_start=message_start,
                                             message_end=message_end))
                message = get_messages(dbquery,
                                       limit.getint("messages"))
                errors = ErrorResponse("OK")
                logger.success("\'_all_messages\' executed successfully")
            else:
                flow.append(api.FlowResponse(uuid=flow_uuid,
                                             message_start=message_start,
                                             message_end=MESSAGE_COUNT))
                if message_volume <= limit.getint("messages"):
                    message = get_messages(dbquery,
                                           request.data.flow[0].message_end,
                                           request.data.flow[0].message_start)
                    logger.success("\'_all_messages\' executed successfully")
                    errors = ErrorResponse("PARTIAL_CONTENT")
                else:
                    errors = ErrorResponse("FORBIDDEN",
                                           "Requested more messages"
                                           f" than server limit"
                                           f" (<{limit.getint('messages')})")

        data = api.DataResponse(time=self.get_time,
                                flow=flow,
                                message=message)

        return api.Response(type=request.type,
                            data=data,
                            errors=errors.result(),
                            jsonapi=self.jsonapi)

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
            errors = ErrorResponse("BAD_REQUEST",
                                   "Wrong flow type")
        elif flow_type == 'chat' and len(users) != 2:
            errors = ErrorResponse("BAD_REQUEST",
                                   "Must be two users only")
        else:
            try:
                self._db.add_flow(flow_uuid,
                                  users,
                                  self.get_time,
                                  flow_type,
                                  request.data.flow[0].title,
                                  request.data.flow[0].info,
                                  owner)
            except DatabaseWriteError as flow_error:
                errors = ErrorResponse("NOT_FOUND",
                                       str(flow_error))
            else:
                flow.append(api.FlowResponse(uuid=flow_uuid,
                                             time=self.get_time,
                                             type=request.data.flow[0].type,
                                             title=request.data.flow[0].title,
                                             info=request.data.flow[0].info,
                                             owner=owner,
                                             users=users))
                errors = ErrorResponse("OK")
                logger.success("\'_add_flow\' executed successfully")

        data = api.DataResponse(time=self.get_time,
                                flow=flow)

        return api.Response(type=request.type,
                            data=data,
                            errors=errors.result(),
                            jsonapi=self.jsonapi)

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
                            uuid=element.uuid,
                            time=element.timeCreated,
                            type=element.flowType,
                            title=element.title,
                            info=element.info,
                            owner=element.owner,
                            users=[item.uuid for item in element.users]))
            errors = ErrorResponse("OK")
            logger.success("\'_all_flow\' executed successfully")
        else:
            errors = ErrorResponse("NOT_FOUND")

        data = api.DataResponse(time=self.get_time,
                                flow=flow)

        return api.Response(type=request.type,
                            data=data,
                            errors=errors.result(),
                            jsonapi=self.jsonapi)

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
                    errors = ErrorResponse("UNKNOWN_ERROR",
                                           str(user_info_error))
                else:
                    user.append(api.UserResponse(uuid=dbquery.uuid,
                                                 login=dbquery.login,
                                                 username=dbquery.username,
                                                 avatar=dbquery.avatar,
                                                 bio=dbquery.bio,
                                                 is_bot=dbquery.isBot))
            errors = ErrorResponse("OK")
            logger.success("\'_user_info\' executed successfully")
        else:
            errors = ErrorResponse("FORBIDDEN",
                                   f"Requested more {limit.get('users')}"
                                   " users than server limit")

        data = api.DataResponse(time=self.get_time,
                                user=user)

        return api.Response(type=request.type,
                            data=data,
                            errors=errors.result(),
                            jsonapi=self.jsonapi)

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
                user.append(api.UserResponse(uuid=dbquery.uuid,
                                             auth_id=dbquery.authId))
                errors = ErrorResponse("OK")
                logger.success("\'_authentification\' executed successfully")
            else:
                errors = ErrorResponse("UNAUTHORIZED")
        else:
            errors = ErrorResponse("NOT_FOUND")

        data = api.DataResponse(time=self.get_time,
                                user=user)

        return api.Response(type=request.type,
                            data=data,
                            errors=errors.result(),
                            jsonapi=self.jsonapi)

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
            errors = ErrorResponse("NOT_FOUND",
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
            errors = ErrorResponse("OK")
            logger.success("\'_delete_user\' executed successfully")

        return api.Response(type=request.type,
                            data=None,
                            errors=errors.result(),
                            jsonapi=self.jsonapi)

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
            errors = ErrorResponse("NOT_FOUND",
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
            errors = ErrorResponse("OK")
            logger.success("\'_delete_message\' executed successfully")

        return api.Response(type=request.type,
                            data=None,
                            errors=errors.result(),
                            jsonapi=self.jsonapi)

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
            errors = ErrorResponse("NOT_FOUND",
                                   str(not_found))
        else:
            dbquery.text = request.data.message[0].text
            dbquery.editedTime = self.get_time
            dbquery.editedStatus = True
            errors = ErrorResponse("OK")
            logger.success("\'_edited_message\' executed successfully")

        return api.Response(type=request.type,
                            data=None,
                            errors=errors.result(),
                            jsonapi=self.jsonapi)

    def _ping_pong(self,
                   request: api.Request) -> api.Response:
        """Generates a response to a client's request
        for communication between server and client.
        """
        errors = ErrorResponse("OK")
        logger.success("\'_ping_pong\' executed successfully")

        return api.Response(type=request.type,
                            data=None,
                            errors=errors.result(),
                            jsonapi=self.jsonapi)

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

        errors = ErrorResponse(status,
                               add_info)
        logger.success("\'_errors\' executed successfully")

        return api.Response(type=response,
                            data=None,
                            errors=errors.result(),
                            jsonapi=self.jsonapi)
