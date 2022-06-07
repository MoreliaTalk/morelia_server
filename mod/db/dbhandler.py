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

from collections import namedtuple
import inspect
import sys
from typing import Any, Optional

import sqlobject as orm
from sqlobject import SQLObject
from sqlobject.main import SQLObjectIntegrityError
from sqlobject.main import SQLObjectNotFound
from sqlobject.sqlbuilder import AND
from sqlobject.sresults import SelectResults

from mod.config.config import ConfigHandler
from mod.db import models


class DatabaseReadError(SQLObjectNotFound):
    """
    Occurs when there is no table in the database.
    There was a problem at the stage of reading from database.
    """


class DatabaseAccessError(Exception):
    """
    Occurs when there is an unknown problem when reading from database.
    """


class DatabaseWriteError(SQLObjectNotFound):
    """
    Occurs when there is an unknown problem when writing to database.
    """


class DBHandler:
    """
    A layer for interaction with the database ORM.
    As a method prescribed frequently used actions with data from database.

    Args:
        uri: [name of DB-API]:/:[directory or url or 'memory'] like that
             sqlite:/:memory:
        debug: enable or disable debug messages
        logger: name of logger
        loglevel: standard logging levels: info, debug, error.
                  or stderr, stdout
        path_to_models: path to the location of the file describing
                        database tables
    """

    __instance: Optional[ConfigHandler] = None
    _logger: Optional[str]
    _loglevel: Optional[str]

    def __new__(cls, *args, **kwargs):
        """
        A function called when creating a new object.

        If such an object already exists, returns it.
        And if not, creates a new one.

        Args:
            cls(ConfigHandler): class ConfigHandler
            *args:
            **kwargs:
        """

        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self,
                 uri: str = 'sqlite:/:memory:',
                 debug: bool = False,
                 logger: str = 'stderr',
                 loglevel: str = 'critical',
                 path_to_models: str = "mod.db.models") -> None:
        self.uri = uri

        if debug:
            self._debug = "1"
            self._logger = logger
            self._loglevel = loglevel
            self._uri = "".join((uri,
                                 f"?debug={self._debug}",
                                 f"&logger={self._logger}",
                                 f"&loglevel={self._loglevel}"))
        else:
            self._debug = "0"
            self._logger = None
            self._loglevel = None
            self._uri = "".join((uri,
                                 f"?debug={self._debug}"))

        self.connection = orm.connectionForURI(self._uri)
        orm.sqlhub.processConnection = self.connection
        self.path = path_to_models

    def __str__(self) -> str:
        """
        Returned string which contains URI for connected database.
        """

        return f"Connected to database: {self._uri}"

    def __repr__(self) -> str:
        """
        Return class name and parameters send to class when is created.
        """

        return "".join((f"Class {self.__class__.__name__}: ",
                        f"debug={self._debug} ",
                        f"logger={self._logger} ",
                        f"loglevel={self._loglevel}"))

    def __search_db_in_models(self) -> tuple:
        """
        Search all class name which contains in models.

        Returns:
            name of table
        """

        classes = [cls_name for cls_name, cls_obj
                   in inspect.getmembers(sys.modules[self.path])
                   if inspect.isclass(cls_obj)]
        return tuple(classes)

    def create_table(self) -> None:
        """
        Create all table which contains in models.
        """

        for item in self.__search_db_in_models():
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True,
                               connection=self.connection)
        return

    def delete_table(self) -> None:
        """
        Delete all table which contains in models.
        """

        for item in self.__search_db_in_models():
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True,
                             connection=self.connection)
        return

    @property
    def debug(self) -> bool:
        """
        Shows is flag set in property `debug`.

        Returns:
            True or False
        """

        if self._debug == "0":
            return False
        else:
            return True

    @debug.setter
    def debug(self,
              value: bool = False) -> None:
        """
        Set `debug` property.

        Args:
            value: True or False
        """

        if value:
            self._debug = "1"
            self._uri = "".join((self.uri,
                                 f"?debug={self._debug}"))
        else:
            self._debug = "0"
            self._uri = "".join((self.uri,
                                 f"?debug={self._debug}"))
        self.connection = orm.connectionForURI(self._uri)
        orm.sqlhub.processConnection = self.connection

    def __read_db(self,
                  table: str,
                  get_one: bool,
                  **kwargs) -> SelectResults | SQLObject:
        """
        Universal method for read data in database.

        Args:
            table: name of table
            get_one: sets how many objects will be returned, True for one
                           object or False for many object
            **kwargs: dict contains name of column and data

        Returns:
            ORM object contains one or many row from database

        Raises:
            DatabaseReadError: occurs when there is no table in the database,
                               there was a problem at the stage of reading from
                               database
            DatabaseAccessError: occurs when there is an unknown problem when
                                 reading from database
        """

        # The SelectResults object type when the result
        # is in the form of a list. SQLObject type when
        # the result is a single object.
        db = getattr(models, table)
        if get_one:
            try:
                dbquery = db.selectBy(self.connection,
                                      **kwargs).getOne()
            except (SQLObjectNotFound, SQLObjectIntegrityError) as err:
                raise DatabaseReadError(err)
            except Exception as err:
                raise DatabaseAccessError(err)
            else:
                return dbquery
        else:
            try:
                dbquery = db.selectBy(self.connection,
                                      **kwargs)
            except SQLObjectNotFound as err:
                raise DatabaseReadError(err)
            except Exception as err:
                raise DatabaseAccessError(err)
            else:
                return dbquery

    @staticmethod
    def __write_db(table: str,
                   **kwargs) -> SQLObject:
        """
        Universal method for write data in database.

        Args:
            table: name of table
            **kwargs: dict contains name of column and data

        Returns:
            (SQLObject):

        Raises:
            DatabaseWriteError: occurs when there is an unknown problem when
                                writing to database
        """

        db = getattr(models, table)
        try:
            dbquery = db(**kwargs)
        except (Exception, SQLObjectIntegrityError) as err:
            raise DatabaseWriteError(err)
        else:
            return dbquery

    def get_all_user(self) -> SelectResults:
        """
        Gives out all user contains in UserConfig table.

        Returns:
            (SelectResult):
        """

        return self.__read_db(table="UserConfig",
                              get_one=False)

    def get_user_by_uuid(self,
                         uuid: str) -> SQLObject:
        """
        Gives out user by uuid contains in UserConfig table.

        Args:
            uuid: unique user identify number

        Returns:
            (SQLObject):
        """

        return self.__read_db(table="UserConfig",
                              get_one=True,
                              uuid=uuid)

    def get_user_by_login(self,
                          login: str) -> SQLObject:
        """
        Gives out user by login contains in UserConfig table.

        Args:
            login: user login

        Returns:
            (SQLObject):
        """

        return self.__read_db(table="UserConfig",
                              get_one=True,
                              login=login)

    def get_user_by_login_and_password(self,
                                       login: str,
                                       password: str) -> SQLObject:
        """
        Gives out user by login and password contains in UserConfig table.

        Args:
            login: user login
            password: user password

        Returns:
            (SQLObject):
        """

        return self.__read_db(table="UserConfig",
                              get_one=True,
                              login=login,
                              password=password)

    def add_user(self,
                 uuid: str,
                 login: str,
                 password: str,
                 hash_password: str = None,
                 username: str = None,
                 is_bot: bool = False,
                 auth_id: str = None,
                 token_ttl: int = None,
                 email: str = None,
                 avatar: bytes = None,
                 bio: str = None,
                 salt: bytes = None,
                 key: bytes = None) -> SQLObject:
        """
        Added new user to the UserConfig table.
        If salt or key is None then used blank string converted to bytes.

        Args:
            uuid: unique user identify number
            login: user login
            password: user password
            hash_password: hash from password
            username: public username
            is_bot: type of user
            auth_id: authenticate token
            token_ttl: time to live auth_id token
            email: user email
            avatar: user image or photo
            bio: text information about user
            salt: secret bytes string
            key: secrets bytes string

        Returns:
            (SQLObject):
        """

        if salt is None:
            salt = b''

        if key is None:
            key = b''

        return self.__write_db(table="UserConfig",
                               uuid=uuid,
                               login=login,
                               password=password,
                               hash_password=hash_password,
                               username=username,
                               is_bot=is_bot,
                               auth_id=auth_id,
                               token_ttl=token_ttl,
                               email=email,
                               avatar=avatar,
                               bio=bio,
                               salt=salt,
                               key=key)

    def update_user(self,
                    uuid: str,
                    login: str = None,
                    password: str = None,
                    hash_password: str = None,
                    username: str = None,
                    is_bot: bool = False,
                    auth_id: str = None,
                    token_ttl: int = None,
                    email: str = None,
                    avatar: bytes = None,
                    bio: str = None,
                    key: bytes = None,
                    salt: bytes = None) -> str:
        """
        Updating information in the table UserConfig.

        Args:
            uuid: unique user identify number
            login: user login
            password: user password
            hash_password: hash from password
            username: public username
            is_bot: type of user
            auth_id: authenticate token
            token_ttl: time to live auth_id token
            email: user email
            avatar: user image or photo
            bio: text information about user
            salt: secret bytes string
            key: secrets bytes string

        Returns:
            "Updated" message
        """

        dbquery = self.__read_db(table="UserConfig",
                                 get_one=True,
                                 uuid=uuid)
        if login:
            dbquery.login = login

        if password:
            dbquery.password = password

        if hash_password:
            dbquery.hash_password = hash_password

        if username:
            dbquery.username = username

        if is_bot:
            dbquery.is_bot = is_bot

        if auth_id:
            dbquery.auth_id = auth_id

        if token_ttl:
            dbquery.token_ttl = token_ttl

        if email:
            dbquery.email = email

        if avatar:
            dbquery.avatar = avatar

        if bio:
            dbquery.bio = bio

        if key:
            dbquery.key = key

        if salt:
            dbquery.salt = salt

        return "Updated"

    def get_all_message(self) -> SelectResults:
        """
        Gives out all message contains Message table.

        Returns:
            (SelectResults):
        """

        return self.__read_db(table="Message",
                              get_one=False)

    def get_message_by_uuid(self,
                            uuid: str) -> SQLObject:
        """
        Gives out one message by uuid which contains in Message table.

        Args:
            uuid: unique user identify number

        Returns:
            (SQLObject):
        """

        return self.__read_db(table="Message",
                              get_one=True,
                              uuid=uuid)

    def get_message_by_text(self,
                            text: str) -> SelectResults:
        """
        Gives out all message which contains desired text string.

        Args:
            text: text string to be found

        Returns:
            (SelectResults):
        """

        return self.__read_db(table="Message",
                              get_one=False,
                              text=text)

    @staticmethod
    def get_message_by_exact_time(time: int) -> SelectResults:
        """
        Gives out message by time == requested time.

        Args:
            time: Unix-like time

        Returns:
            (SelectResults):
        """

        return models.Message.select(models.Message.q.time == time)

    @staticmethod
    def get_message_by_less_time(time: int) -> SelectResults:
        """
        Gives out message by time <= requested time.

        Args:
            time: Unix-like time

        Returns:
            (SelectResults):
        """

        return models.Message.select(models.Message.q.time <= time)

    @staticmethod
    def get_message_by_more_time(time: int) -> SelectResults:
        """
        Gives out message by time >= requested time.

        Args:
            time: Unix-like time

        Returns:
            (SelectResults):
        """

        return models.Message.select(models.Message.q.time >= time)

    def get_message_by_more_time_and_flow(self,
                                          flow_uuid: str,
                                          time: int) -> SelectResults:
        """
        Gives out message by flow and time >= than requested.

        Args:
            flow_uuid: unique identify number from flow
            time: Unix-like time

        Returns:
            (SelectResults):
        """

        flow = self.__read_db(table="Flow",
                              get_one=True,
                              uuid=flow_uuid)
        return models.Message.select(
            AND(models.Message.q.flow == flow,
                models.Message.q.time >= time))

    def get_message_by_less_time_and_flow(self,
                                          flow_uuid: str,
                                          time: int) -> SelectResults:
        """
        Gives out message by flow and time <= requested time.

        Args:
            flow_uuid: unique identify number from flow
            time: Unix-like time

        Returns:
            (SelectResults):
        """

        flow = self.__read_db(table="Flow",
                              get_one=True,
                              uuid=flow_uuid)
        return models.Message.select(
            AND(models.Message.q.flow == flow,
                models.Message.q.time <= time))

    def get_message_by_exact_time_and_flow(self,
                                           flow_uuid: str,
                                           time: int) -> SelectResults:
        """
        Gives out message by flow and time == requested time.

        Args:
            flow_uuid: unique identify number from flow
            time: Unix-like time

        Returns:
            (SelectResults):
        """

        flow = self.__read_db(table="Flow",
                              get_one=True,
                              uuid=flow_uuid)
        return models.Message.select(
            AND(models.Message.q.flow == flow,
                models.Message.q.time == time))

    def add_message(self,
                    flow_uuid: str,
                    user_uuid: str,
                    message_uuid: str,
                    time: int,
                    text: str = None,
                    picture: bytes = None,
                    video: bytes = None,
                    audio: bytes = None,
                    document: bytes = None,
                    emoji: bytes = None) -> SQLObject:
        """
        Added new message to the Message table.

        Notes:
            Before adding a message to the "Message" table, the presence of
            "flow" and "user" in the database is checked.

        Args:
            flow_uuid: unique identify number from flow
            user_uuid: unique user identify number
            message_uuid: unique identify number from message
            time: Unix-like time
            text: message text
            picture: appending image
            video: appending video
            audio: appending audio
            document: appending document
            emoji: appending emoji image

        Returns:
            (SQLObject):
        """

        flow = self.__read_db(table="Flow",
                              get_one=True,
                              uuid=flow_uuid)
        user = self.__read_db(table="UserConfig",
                              get_one=True,
                              uuid=user_uuid)
        return self.__write_db(table="Message",
                               uuid=message_uuid,
                               text=text,
                               time=time,
                               file_picture=picture,
                               file_video=video,
                               file_audio=audio,
                               file_document=document,
                               emoji=emoji,
                               edited_time=None,
                               edited_status=False,
                               user=user,
                               flow=flow)

    def update_message(self,
                       uuid: str,
                       text: str = None,
                       picture: bytes = None,
                       video: bytes = None,
                       audio: bytes = None,
                       document: bytes = None,
                       emoji: bytes = None,
                       edited_time: int = None,
                       edited_status: bool = False) -> str:
        """
        Update message content which contains in Message table.

        Args:
            uuid: unique identify number from message
            text: message text
            picture: appending image
            video: appending video
            audio: appending audio
            document: appending document
            emoji: appending emoji image
            edited_time: time when user last time is corrected his message
            edited_status: True if user corrected his message

        Returns:
            "Updated" message
        """

        dbquery = self.__read_db(table="Message",
                                 get_one=True,
                                 uuid=uuid)
        if text:
            dbquery.text = text

        if picture:
            dbquery.file_picture = picture

        if video:
            dbquery.file_video = video

        if audio:
            dbquery.file_audio = audio

        if document:
            dbquery.file_document = document

        if emoji:
            dbquery.emoji = emoji

        if edited_time:
            dbquery.edited_time = edited_time

        if edited_status:
            dbquery.edited_status = edited_status

        return "Updated"

    def get_all_flow(self) -> SelectResults:
        """
        Gives out all flow from Flow table.

        Returns:
            (SelectResults):
        """

        return self.__read_db(table="Flow",
                              get_one=False)

    def get_flow_by_uuid(self,
                         uuid: str) -> SQLObject:
        """
        Gives out one flow by uuid from Flow table.

        Args:
            uuid: unique user identify number

        Returns:
            (SQLObject):
        """

        return self.__read_db(table="Flow",
                              get_one=True,
                              uuid=uuid)

    def get_flow_by_title(self,
                          title: str) -> SelectResults:
        """
        Gives out flow by title which contains in Flow table.

        Args:
            title: name added in public information about flow

        Returns:
            (SelectResults):
        """

        return self.__read_db(table="Flow",
                              get_one=False,
                              title=title)

    @staticmethod
    def get_flow_by_more_time(time: int) -> SelectResults:
        """
        Gives flow by time => requested time.

        Args:
            time: Unix-like time

        Returns:
            (SelectResults):
        """

        return models.Flow.select(models.Flow.q.time_created >= time)

    @staticmethod
    def get_flow_by_less_time(time: int) -> SelectResults:
        """
        Gives out flow by time <= requested time.

        Args:
            time: Unix-like time

        Returns:
            (SelectResults):
        """

        return models.Flow.select(models.Flow.q.time_created <= time)

    @staticmethod
    def get_flow_by_exact_time(time: int) -> SelectResults:
        """
        Gives out flow by time == requested time.

        Args:
            time: Unix-like time

        Returns:
            (SelectResults):
        """

        return models.Flow.select(models.Flow.q.time_created == time)

    def add_flow(self,
                 uuid: str,
                 users: list | tuple,
                 time_created: int = None,
                 flow_type: str = None,
                 title: str = None,
                 info: str = None,
                 owner: str = None) -> SQLObject:
        """
        Added new flow to the Flow table.

        Args:
            uuid: unique identify number from flow
            users: uuid user which used that flow
            time_created: time when created flow
            flow_type: ``chat`` or ``group`` or ``channel``
            title: name added in public information about flow
            info: text added in public information about flow
            owner: user uuid which created that flow

        Returns:
            (SQLObject):
        """

        dbquery = self.__write_db(table="Flow",
                                  uuid=uuid,
                                  time_created=time_created,
                                  flow_type=flow_type,
                                  title=title,
                                  info=info,
                                  owner=owner)
        for user_uuid in users:
            dbquery.addUserConfig(self.__read_db(table="UserConfig",
                                                 get_one=True,
                                                 uuid=user_uuid))
        return dbquery

    def update_flow(self,
                    uuid: str,
                    flow_type: str = None,
                    title: str = None,
                    info: str = None,
                    owner: str = None) -> str:
        """
        Update information about flow which contains in Flow table.

        Args:
            uuid: unique identify number from flow
            flow_type: ``chat`` or ``group`` or ``channel``
            title: name added in public information about flow
            info: text added in public information about flow
            owner: user uuid which created that flow

        Returns:
            "Updated" message
        """

        dbquery = self.__read_db(table="Flow",
                                 get_one=True,
                                 uuid=uuid)

        if flow_type:
            dbquery.flow_type = flow_type

        if title:
            dbquery.title = title

        if info:
            dbquery.info = info

        if owner:
            dbquery.owner = owner

        return "Updated"

    def get_table_count(self) -> Any:
        """
        Gives out quantity all row from Message, Flow or UserConfig table.

        Returns:
            (namedtuple): where

                          ``user_count`` - quantity all UserConfig row

                          ``flow_count`` - quantity all Flow row

                          ``message_count`` - quantity all Message row
        """

        TableCount = namedtuple('TableCount', ["user_count",
                                               "flow_count",
                                               "message_count"])
        user = self.__read_db(table="UserConfig",
                              get_one=False)
        flow = self.__read_db(table="Flow",
                              get_one=False)
        message = self.__read_db(table="Message",
                                 get_one=False)
        return TableCount(user.count(),
                          flow.count(),
                          message.count())

    def get_all_admin(self) -> SelectResults:
        """
        Gives out all users from Admin table.

        Returns:
            (SelectResults):
        """

        return self.__read_db(table="Admin",
                              get_one=False)

    def get_admin_by_name(self,
                          username: str) -> SQLObject:
        """
        Gives user by name from Admin table.

        Args:
            username: name user which granted administrator rights

        Returns:
            (SQLObject):
        """

        return self.__read_db(table="Admin",
                              get_one=True,
                              username=username)

    def add_admin(self,
                  username: str,
                  hash_password: str) -> SQLObject:
        """
        Added new admin to the Admin table.

        Args:
            username: name user which granted administrator rights
            hash_password: hash-function generated from administrator password

        Returns:
            (SQLObject):
        """

        return self.__write_db(table="Admin",
                               username=username,
                               hash_password=hash_password)
