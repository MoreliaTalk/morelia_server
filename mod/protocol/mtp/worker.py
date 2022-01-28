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
from collections import namedtuple

from pydantic import ValidationError
from loguru import logger

from mod.protocol.mtp import api
from mod import error
from mod import lib
from mod.db.dbhandler import DBHandler
from mod.db.dbhandler import DatabaseWriteError
from mod.db.dbhandler import DatabaseReadError
from mod.db.dbhandler import DatabaseAccessError
from mod.config import SERVER_LIMIT as LIMIT


class MTPErrorResponse:
    """Catcher errors in "try...except" content.
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
            logger.debug(f"Status code({catch_error.code}):",
                         f" {catch_error.status}")
            code = catch_error.code
            status = catch_error.status
            time_ = int(time())
            if self.detail is None:
                detail = catch_error.detail
            else:
                detail = self.detail

        return api.ErrorsResponse(code=code,
                                  status=status,
                                  time=time_,
                                  detail=detail)


class MTProtocol:
    """Processing requests and forming answers according to "MTP" protocol.
    Protocol version and its actual description:
    https://github.com/MoreliaTalk/morelia_protocol/blob/master/README.md

    Args:
        request: JSON request from websocket client
        database (DBHandler): object - database connection point
        
    Returns:
        returns class api.Response
    """
    def __init__(self,
                 request,
                 database: DBHandler):
        self.jsonapi = api.VersionResponse(version=api.VERSION,
                                           revision=api.REVISION)
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
            auth = self._check_auth(self.request.data.user[0].uuid,
                                    self.request.data.user[0].auth_id)
            if auth.result:
                match self.request.type:
                    case "get_update":
                        self.response = self._get_update(self.request)
                    case "send_message":
                        self.response = self._send_message(self.request)
                    case "all_messages":
                        self.response = self._all_messages(self.request)
                    case "add_flow":
                        self.response = self._add_flow(self.request)
                    case "all_flow":
                        self.response = self._all_flow(self.request)
                    case "user_info":
                        self.response = self._user_info(self.request)
                    case "delete_user":
                        self.response = self._delete_user(self.request)
                    case "delete_message":
                        self.response = self._delete_message(self.request)
                    case "edited_message":
                        self.response = self._edited_message(self.request)
                    case "ping_pong":
                        self.response = self._ping_pong(self.request)
                    case _:
                        self.response = self._errors("METHOD_NOT_ALLOWED")
            else:
                match self.request.type:
                    case 'register_user':
                        self.response = self._register_user(self.request)
                    case 'authentication':
                        self.response = self._authentication(self.request)
                    case _:
                        self.response = self._errors("UNAUTHORIZED",
                                                     auth.error_message)

    def _check_auth(self,
                    uuid: str,
                    auth_id: str) -> namedtuple:
        Result = namedtuple('Result', ['result',
                                       'error_message'])
        try:
            dbquery = self._db.get_user_by_uuid(uuid)
            logger.success("User was found in the database")
        except DatabaseReadError:
            message = "User was not authenticated"
            logger.debug(message)
            return Result(False,
                          message)
        else:
            if auth_id == dbquery.auth_id:
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
            result = self.response.json()
            return result
        else:
            result = response.json()
            return result

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
        Note: This version also authentication user, that exist in database
        """
        uuid = str(uuid4().int)
        password = request.data.user[0].password
        login = request.data.user[0].login
        username = request.data.user[0].username
        email = request.data.user[0].email
        user = []
        data = None

        if self._check_login(login):
            errors = MTPErrorResponse("CONFLICT")
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
                              token_ttl=self.get_time,
                              email=email,
                              avatar=None,
                              bio=None,
                              salt=generated.get_salt,
                              key=generated.get_key)
            user.append(api.UserResponse(uuid=uuid,
                                         auth_id=auth_id,
                                         token_ttl=self.get_time))
            data = api.DataResponse(time=self.get_time,
                                    user=user)
            errors = MTPErrorResponse("CREATED")
            logger.success("User is register")

        return api.Response(type=request.type,
                            data=data,
                            errors=errors.result(),
                            jsonapi=self.jsonapi)

    def _get_update(self,
                    request: api.Request) -> api.Response:
        """Provides updates of flows, messages and users in them from time
        """
        # select all fields of the user table
        # TODO внести изменения в протокол, добавить фильтр
        # по дате создания пользователя
        message = []
        flow = []
        user = []

        dbquery_user = self._db.get_all_user()
        dbquery_flow = self._db.get_flow_by_more_time(request.data.time)
        dbquery_message = self._db.get_message_by_more_time(request.data.time)

        if dbquery_message.count() >= 1:
            for element in dbquery_message:
                message.append(api.MessageResponse(
                               uuid=element.uuid,
                               client_id=None,
                               text=element.text,
                               from_user=element.user.uuid,
                               time=element.time,
                               from_flow=element.flow.uuid,
                               file_picture=element.file_picture,
                               file_video=element.file_video,
                               file_audio=element.file_audio,
                               file_document=element.file_document,
                               emoji=element.emoji,
                               edited_time=element.edited_time,
                               edited_status=element.edited_status))

        if dbquery_flow.count() >= 1:
            for element in dbquery_flow:
                flow.append(api.FlowResponse(
                            uuid=element.uuid,
                            time=element.time_created,
                            type=element.flow_type,
                            title=element.title,
                            info=element.info,
                            owner=element.owner,
                            users=[item.uuid for item in element.users]))

        if dbquery_user.count() >= 1:
            for element in dbquery_user:
                user.append(api.UserResponse(
                            uuid=element.uuid,
                            username=element.username,
                            is_bot=element.is_bot,
                            avatar=element.avatar,
                            bio=element.bio))

        errors = MTPErrorResponse("OK")
        data = api.DataResponse(time=self.get_time,
                                flow=flow,
                                message=message,
                                user=user)
        logger.success("\'_get_update\' executed successfully")

        return api.Response(type=request.type,
                            data=data,
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
        except (DatabaseWriteError,
                DatabaseReadError) as ERROR:
            errors = MTPErrorResponse("NOT_FOUND",
                                      str(ERROR))
        else:
            message.append(api.MessageResponse(uuid=message_uuid,
                                               client_id=client_id,
                                               from_user=user_uuid,
                                               from_flow=flow_uuid))
            data = api.DataResponse(time=self.get_time,
                                    message=message)
            logger.success("\'_send_message\' executed successfully")
            errors = MTPErrorResponse("OK")

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
                         start: int = 0) -> list[api.MessageResponse]:
            _list = []
            for element in db[start:end]:
                _list.append(api.MessageResponse(
                               uuid=element.uuid,
                               client_id=None,
                               text=element.text,
                               from_user=element.user.uuid,
                               time=element.time,
                               from_flow=element.flow.uuid,
                               file_picture=element.file_picture,
                               file_video=element.file_video,
                               file_audio=element.file_audio,
                               file_document=element.file_document,
                               emoji=element.emoji,
                               edited_time=element.edited_time,
                               edited_status=element.edited_status))
            return _list

        try:
            dbquery = self._db.get_message_by_more_time_and_flow(flow_uuid,
                                                                 request.data.time)
            MESSAGE_COUNT = dbquery.count()
            dbquery[0]
        except DatabaseReadError as flow_error:
            errors = MTPErrorResponse("NOT_FOUND",
                                      str(flow_error))
        else:
            if MESSAGE_COUNT <= LIMIT.getint("messages"):
                flow.append(api.FlowResponse(uuid=flow_uuid,
                                             message_start=message_start,
                                             message_end=message_end))
                message = get_messages(dbquery,
                                       LIMIT.getint("messages"))
                errors = MTPErrorResponse("OK")
                logger.success("\'_all_messages\' executed successfully")
            else:
                flow.append(api.FlowResponse(uuid=flow_uuid,
                                             message_start=message_start,
                                             message_end=MESSAGE_COUNT))
                if message_volume <= LIMIT.getint("messages"):
                    message = get_messages(dbquery,
                                           request.data.flow[0].message_end,
                                           request.data.flow[0].message_start)
                    logger.success("\'_all_messages\' executed successfully")
                    errors = MTPErrorResponse("PARTIAL_CONTENT")
                else:
                    errors = MTPErrorResponse("FORBIDDEN",
                                              "Requested more messages"
                                              f" than server limit"
                                              f" ({LIMIT.getint('messages')})")

        data = api.DataResponse(time=self.get_time,
                                flow=flow,
                                message=message)

        return api.Response(type=request.type,
                            data=data,
                            errors=errors.result(),
                            jsonapi=self.jsonapi)

    def _add_flow(self,
                  request: api.Request) -> api.Response:
        """Allows to add a new flow to database
        """
        flow_uuid = str(uuid4().int)
        owner = request.data.flow[0].owner
        users = request.data.flow[0].users
        flow_type = request.data.flow[0].type
        flow = []

        if flow_type not in ["chat",
                             "group",
                             "channel"]:
            errors = MTPErrorResponse("BAD_REQUEST",
                                      "Wrong flow type")
        elif flow_type == 'chat' and len(users) != 2:
            errors = MTPErrorResponse("BAD_REQUEST",
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
                errors = MTPErrorResponse("NOT_FOUND",
                                          str(flow_error))
            else:
                flow.append(api.FlowResponse(uuid=flow_uuid,
                                             time=self.get_time,
                                             type=request.data.flow[0].type,
                                             title=request.data.flow[0].title,
                                             info=request.data.flow[0].info,
                                             owner=owner,
                                             users=users))
                errors = MTPErrorResponse("OK")
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
                            time=element.time_created,
                            type=element.flow_type,
                            title=element.title,
                            info=element.info,
                            owner=element.owner,
                            users=[item.uuid for item in element.users]))
            errors = MTPErrorResponse("OK")
            logger.success("\'_all_flow\' executed successfully")
        else:
            errors = MTPErrorResponse("NOT_FOUND")

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

        if users_volume <= LIMIT.getint("users"):
            errors = MTPErrorResponse("OK")
            for element in request.data.user[1:]:
                try:
                    dbquery = self._db.get_user_by_uuid(element.uuid)
                except (DatabaseReadError,
                        DatabaseAccessError) as user_info_error:
                    errors = MTPErrorResponse("UNKNOWN_ERROR",
                                              str(user_info_error))
                else:
                    user.append(api.UserResponse(uuid=dbquery.uuid,
                                                 login=dbquery.login,
                                                 username=dbquery.username,
                                                 avatar=dbquery.avatar,
                                                 bio=dbquery.bio,
                                                 is_bot=dbquery.is_bot))
            logger.success("\'_user_info\' executed successfully")
        else:
            errors = MTPErrorResponse("FORBIDDEN",
                                      f"Requested more {LIMIT.get('users')}"
                                      " users than server limit")

        data = api.DataResponse(time=self.get_time,
                                user=user)

        return api.Response(type=request.type,
                            data=data,
                            errors=errors.result(),
                            jsonapi=self.jsonapi)

    def _authentication(self,
                        request: api.Request) -> api.Response:
        """Performs authentication of registered client,
        with issuance of a unique hash number of connection session.
        During authentication password transmitted by client
        and password contained in server database are verified.
        """
        login = request.data.user[0].login
        password = request.data.user[0].password
        user = []

        if self._check_login(login):
            dbquery = self._db.get_user_by_login(login)
            # to check password, we use same module as for its
            # hash generation. Specify password entered by user
            # and hash of old password as parameters.
            # After that, hashes are compared using "check_password" method.
            generator = lib.Hash(password,
                                 dbquery.uuid,
                                 dbquery.salt,
                                 dbquery.key,
                                 dbquery.hash_password)
            if generator.check_password():
                dbquery.auth_id = generator.auth_id()
                user.append(api.UserResponse(uuid=dbquery.uuid,
                                             auth_id=dbquery.auth_id))
                errors = MTPErrorResponse("OK")
                logger.success("\'_authentication\' executed successfully")
            else:
                errors = MTPErrorResponse("UNAUTHORIZED")
        else:
            errors = MTPErrorResponse("NOT_FOUND")

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
            errors = MTPErrorResponse("NOT_FOUND",
                                      str(not_found))
        else:
            dbquery.login = "User deleted"
            dbquery.password = uuid
            dbquery.hash_password = uuid
            dbquery.username = "User deleted"
            dbquery.auth_id = uuid
            dbquery.email = ""
            dbquery.avatar = b""
            dbquery.bio = "deleted"
            dbquery.salt = b"deleted"
            dbquery.key = b"deleted"
            errors = MTPErrorResponse("OK")
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
            errors = MTPErrorResponse("NOT_FOUND",
                                      str(not_found))
        else:
            dbquery.text = "Message deleted"
            dbquery.file_picture = b''
            dbquery.file_video = b''
            dbquery.file_audio = b''
            dbquery.file_document = b''
            dbquery.emoji = b''
            dbquery.edited_time = self.get_time
            dbquery.edited_status = True
            errors = MTPErrorResponse("OK")
            logger.success("\'_delete_message\' executed successfully")

        return api.Response(type=request.type,
                            data=None,
                            errors=errors.result(),
                            jsonapi=self.jsonapi)

    def _edited_message(self,
                        request: api.Request) -> api.Response:
        """Changes text and time in database Message table.
        Value of edited_status column changes from None to True.
        """
        message_uuid = request.data.message[0].uuid

        try:
            dbquery = self._db.get_message_by_uuid(message_uuid)
        except (DatabaseReadError,
                DatabaseAccessError) as not_found:
            errors = MTPErrorResponse("NOT_FOUND",
                                      str(not_found))
        else:
            dbquery.text = request.data.message[0].text
            dbquery.edited_time = self.get_time
            dbquery.edited_status = True
            errors = MTPErrorResponse("OK")
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
        errors = MTPErrorResponse("OK")
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

        errors = MTPErrorResponse(status,
                                  add_info)
        logger.success("\'_errors\' executed successfully")

        return api.Response(type=response,
                            data=None,
                            errors=errors.result(),
                            jsonapi=self.jsonapi)
