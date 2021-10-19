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

import json
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

        return api.ErrorsResponse(code=code,
                                  status=status,
                                  time=time,
                                  detail=detail)


class User(Error):
    def check_auth(method_to_decorate):
        def wrapper(self, request):
            uuid = request.data.user[0].uuid
            auth_id = request.data.user[0].auth_id

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
                    return method_to_decorate(self, request)
                else:
                    logger.debug("Authentication User failed")
                    return self.catching_error("UNAUTHORIZED")

        return wrapper

    def check_login(self, login: str) -> bool:
        """Checks database for a user with the same login

        Args:
            login (str): user login

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
            user.append(api.UserResponse(uuid=uuid,
                                         auth_id=auth_id))
            data = api.DataResponse(time=self.get_time,
                                    user=user)
            errors = self.catching_error("CREATED")
            logger.success("User is registred")

        return api.Response(type=request.type,
                            data=data,
                            errors=errors,
                            jsonapi=self.jsonapi)

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

        dbquery_user = models.UserConfig.selectBy()
        dbquery_flow = models.Flow.select(models.Flow.q.timeCreated >=
                                          request.data.time)
        dbquery_message = models.Message.select(models.Message.q.time >=
                                                request.data.time)

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
        else:
            message = None

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

        else:
            flow = None

        if dbquery_user.count():
            for element in dbquery_user:
                user.append(api.UserResponse(
                            uuid=element.uuid,
                            username=element.username,
                            is_bot=element.isBot,
                            avatar=element.avatar,
                            bio=element.bio))
        else:
            user = None

        errors = self.catching_error("OK")
        data = api.DataResponse(time=self.get_time,
                                flow=flow,
                                message=message,
                                user=user)
        logger.success("\'_get_update\' executed successfully")

        return api.Response(type=request.type,
                            data=data,
                            errors=errors,
                            jsonapi=self.jsonapi)

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
            flow = models.Flow.selectBy(uuid=flow_uuid).getOne()
            user = models.UserConfig.selectBy(uuid=user_uuid).getOne()
        except SQLObjectNotFound as ERROR:
            errors = self.catching_error("NOT_FOUND",
                                         str(ERROR))
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
            message.append(api.MessageResponse(uuid=message_uuid,
                                               client_id=client_id,
                                               from_flow=flow_uuid,
                                               from_user=user_uuid))
            data = api.DataResponse(time=self.get_time,
                                    message=message)
            logger.success("\'_send_message\' executed successfully")
            errors = self.catching_error("OK")

        return api.Response(type=request.type,
                            data=data,
                            errors=errors,
                            jsonapi=self.jsonapi)

    @User.check_auth
    def _all_messages(self,
                      request: api.Request) -> api.Response:
        """Displays all messages of a specific flow retrieves them
        from database and issues them as an array consisting of JSON
        """
        flow_uuid = request.data.flow[0].uuid
        message_start = request.data.flow[0].message_start
        message_end = request.data.flow[0].message_end
        flow = []
        message = []

        if message_start is None:
            message_start = 0
        if message_end is None:
            message_end = 0
        message_volume = message_end - message_start

        def get_messages(db,
                         end: int,
                         start: int = 0) -> list:
            message = []
            for element in db[start:end]:
                message.append(api.MessageResponse(
                               uuid=element.uuid,
                               client_id=None,
                               from_flow=element.flow.uuid,
                               from_user=element.user.uuid,
                               text=element.text,
                               time=element.time,
                               file_picture=element.filePicture,
                               file_video=element.fileVideo,
                               file_audio=element.fileAudio,
                               file_document=element.fileDocument,
                               emoji=element.emoji,
                               edited_time=element.editedTime,
                               edited_status=element.editedStatus))
            return message

        try:
            flow_dbquery = models.Flow.selectBy(uuid=flow_uuid).getOne()
            dbquery = models.Message.select(
                AND(models.Message.q.flow == flow_dbquery,
                    models.Message.q.time >= request.data.time))
            MESSAGE_COUNT: int = dbquery.count()
            dbquery[0]
        except SQLObjectIntegrityError as flow_error:
            errors = self.catching_error("UNKNOWN_ERROR",
                                         str(flow_error))
        except (IndexError, SQLObjectNotFound) as flow_error:
            errors = self.catching_error("NOT_FOUND",
                                         str(flow_error))
        else:
            if MESSAGE_COUNT <= limit.getint("messages"):
                flow.append(api.FlowResponse(uuid=flow_uuid,
                                             message_start=message_start,
                                             message_end=message_end))
                message = get_messages(dbquery,
                                       limit.getint("messages"))
                errors = self.catching_error("OK")
                logger.success("\'_all_messages\' executed successfully")
            elif MESSAGE_COUNT > limit.getint("messages"):
                flow.append(api.FlowResponse(uuid=flow_uuid,
                                             message_start=message_start,
                                             message_end=MESSAGE_COUNT))
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

        data = api.DataResponse(time=self.get_time,
                                flow=flow,
                                message=message)

        return api.Response(type=request.type,
                            data=data,
                            errors=errors,
                            jsonapi=self.jsonapi)

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

        if flow_type not in ["chat", "group", "channel"]:
            errors = self.catching_error("BAD_REQUEST",
                                         "Wrong flow type")
        elif flow_type == 'chat' and len(users) != 2:
            errors = self.catching_error("BAD_REQUEST",
                                         "Must be two users only")
        else:
            try:
                dbquery = models.Flow(uuid=flow_uuid,
                                      timeCreated=self.get_time,
                                      flowType=flow_type,
                                      title=request.data.flow[0].title,
                                      info=request.data.flow[0].info,
                                      owner=owner)
                for user_uuid in users:
                    user = models.UserConfig.selectBy(uuid=user_uuid).getOne()
                    dbquery.addUserConfig(user)
            except SQLObjectIntegrityError as flow_error:
                errors = self.catching_error("UNKNOWN_ERROR",
                                             str(flow_error))
            else:
                flow.append(api.FlowResponse(uuid=flow_uuid,
                                             time=self.get_time,
                                             type=request.data.flow[0].type,
                                             title=request.data.flow[0].title,
                                             info=request.data.flow[0].info,
                                             owner=owner,
                                             users=users))
                errors = self.catching_error("OK")
                logger.success("\'_add_flow\' executed successfully")

        data = api.DataResponse(time=self.get_time,
                                flow=flow)

        return api.Response(type=request.type,
                            data=data,
                            errors=errors,
                            jsonapi=self.jsonapi)

    @User.check_auth
    def _all_flow(self,
                  request: api.Request) -> api.Response:
        """Allows to get a list of all flows and information about them
        from database
        """
        flow = []
        dbquery = models.Flow.selectBy()

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
            errors = self.catching_error("OK")
            logger.success("\'_all_flow\' executed successfully")
        else:
            errors = self.catching_error("NOT_FOUND")

        data = api.DataResponse(time=self.get_time,
                                flow=flow)

        return api.Response(type=request.type,
                            data=data,
                            errors=errors,
                            jsonapi=self.jsonapi)

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
                    dbquery = models.UserConfig.selectBy(uuid=element.uuid).getOne()
                except SQLObjectIntegrityError as user_info_error:
                    errors = self.catching_error("UNKNOWN_ERROR",
                                                 str(user_info_error))
                else:
                    user.append(api.UserResponse(uuid=dbquery.uuid,
                                                 login=dbquery.login,
                                                 username=dbquery.username,
                                                 is_bot=dbquery.isBot,
                                                 avatar=dbquery.avatar,
                                                 bio=dbquery.bio))
            errors = self.catching_error("OK")
            logger.success("\'_user_info\' executed successfully")
        else:
            errors = self.catching_error("FORBIDDEN",
                                         f"Requested more {limit.get('users')}"
                                         " users than server limit")

        data = api.DataResponse(time=self.get_time,
                                user=user)

        return api.Response(type=request.type,
                            data=data,
                            errors=errors,
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
                user.append(api.UserResponse(uuid=dbquery.uuid,
                                             auth_id=dbquery.authId))
                errors = self.catching_error("OK")
                logger.success("\'_authentification\' executed successfully")
            else:
                errors = self.catching_error("UNAUTHORIZED")
        else:
            errors = self.catching_error("NOT_FOUND")

        data = api.DataResponse(time=self.get_time,
                                user=user)

        return api.Response(type=request.type,
                            data=data,
                            errors=errors,
                            jsonapi=self.jsonapi)

    @User.check_auth
    def _delete_user(self,
                     request: api.Request) -> api.Response:
        """Function irretrievably deletes the user from database.
        """
        uuid = str(uuid4().int)
        login = request.data.user[0].login
        password = request.data.user[0].password

        try:
            dbquery = models.UserConfig.selectBy(login=login,
                                                 password=password).getOne()
        except (SQLObjectIntegrityError, SQLObjectNotFound) as not_found:
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

        return api.Response(type=request.type,
                            data=None,
                            errors=errors,
                            jsonapi=self.jsonapi)

    @User.check_auth
    def _delete_message(self,
                        request: api.Request) -> api.Response:
        """Function deletes the message from database Message
        table by its ID.
        """
        message_uuid = request.data.message[0].uuid

        try:
            dbquery = models.Message.selectBy(uuid=message_uuid).getOne()
        except (SQLObjectIntegrityError, SQLObjectNotFound) as not_found:
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

        return api.Response(type=request.type,
                            data=None,
                            errors=errors,
                            jsonapi=self.jsonapi)

    @User.check_auth
    def _edited_message(self,
                        request: api.Request) -> api.Response:
        """Changes text and time in database Message table.
        Value of editedStatus column changes from None to True.
        """
        message_uuid = request.data.message[0].uuid

        try:
            dbquery = models.Message.selectBy(uuid=message_uuid).getOne()
        except (SQLObjectIntegrityError, SQLObjectNotFound) as not_found:
            errors = self.catching_error("NOT_FOUND",
                                         str(not_found))
        else:
            dbquery.text = request.data.message[0].text
            dbquery.editedTime = self.get_time
            dbquery.editedStatus = True
            errors = self.catching_error("OK")
            logger.success("\'_edited_message\' executed successfully")

        return api.Response(type=request.type,
                            data=None,
                            errors=errors,
                            jsonapi=self.jsonapi)

    @User.check_auth
    def _ping_pong(self,
                   request: api.Request) -> api.Response:
        """Generates a response to a client's request
        for communication between server and client.
        """
        errors = self.catching_error("OK")
        logger.success("\'_ping_pong\' executed successfully")

        return api.Response(type=request.type,
                            data=None,
                            errors=errors,
                            jsonapi=self.jsonapi)

    def _errors(self,
                status: str = None,
                add_info: Exception | str = None,
                request: api.Request = None) -> api.Response:
        """Handles cases when a request to server is not recognized by it.
        Get a standard answer type: error, which contains an object
        with a description of error.
        """
        if request is None:
            response = "error"
        else:
            response = request.type

        if status is None:
            status = "METHOD_NOT_ALLOWED"

        errors = self.catching_error(status, add_info)
        logger.success("\'_errors\' executed successfully")

        return api.Response(type=response,
                            date=None,
                            errors=errors,
                            jsonapi=self.jsonapi)
