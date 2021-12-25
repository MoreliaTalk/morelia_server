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
from typing import Type
from typing import Tuple
import inspect
import sys

import sqlobject as orm
from sqlobject.sqlbuilder import AND
from sqlobject.main import SQLObjectIntegrityError
from sqlobject.main import SQLObjectNotFound
from sqlobject.main import SelectResults
from sqlobject import SQLObject

from mod.db import models


class DatabaseReadError(SQLObjectNotFound):
    pass


class DatabaseAccessError(Exception):
    pass


class DatabaseWriteError(SQLObjectNotFound):
    pass


class DBHandler:

    def __init__(self,
                 uri: str = None,
                 debug: bool = False,
                 logger: str = None,
                 loglevel: str = None,
                 path_to_models: str = "mod.db.models") -> None:
        if uri is None:
            uri = 'sqlite:/:memory:'

        if debug and logger and loglevel:
            self._debug = "1"
            self._logger = logger
            self._loglevel = loglevel
            self._uri = "".join((uri,
                                 f"?debug={self._debug}",
                                 f"?logger={self._logger}",
                                 f"?loglevel={self._loglevel}"))
        else:
            self._uri = uri
            self._debug = "0"
            self._logger = None
            self._loglevel = None

        self.connection = orm.connectionForURI(self._uri)
        orm.sqlhub.processConnection = self.connection
        self.path = path_to_models

    def __str__(self):
        return f"Connected to database: {self._uri}"

    def __repr__(self):
        return "".join((f"class {self.__class__.__name__}: ",
                        f"debug={self._debug} ",
                        f"logger={self._logger} ",
                        f"loglevel={self._loglevel}"))

    def __search_db_in_models(self) -> tuple:
        classes = [cls_name for cls_name, cls_obj
                   in inspect.getmembers(sys.modules[self.path])
                   if inspect.isclass(cls_obj)]
        return tuple(classes)

    def create(self) -> None:
        # looking for all Classes listed in models.py
        for item in self.__search_db_in_models():
            # Create tables in database for each class
            # that is located in models module
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True,
                               connection=self.connection)
        return

    def delete(self) -> None:
        # looking for all Classes listed in models.py
        for item in self.__search_db_in_models():
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True,
                             connection=self.connection)
        return

    @property
    def debug(self) -> bool | None:
        if self._debug == "0":
            return False
        else:
            return True

    @debug.setter
    def debug(self,
              value: bool = False) -> None:
        if value is True:
            self._debug = "1"
        self._uri = "".join((self._uri,
                             f"?debug={self._debug}"))
        self.connection = orm.connectionForURI(self._uri)
        orm.sqlhub.processConnection = self.connection

    def __read_db(self,
                  table: str,
                  get_one: bool,
                  **kwargs) -> SelectResults | SQLObject:
        # The SelectResults object type when the result
        # is in the form of a list. SQLObject type when
        # the result is a single object.
        db = getattr(models, table)
        if get_one:
            try:
                dbquery = db.selectBy(self.connection,
                                      **kwargs).getOne()
            except (SQLObjectNotFound, SQLObjectIntegrityError):
                raise DatabaseReadError
            except Exception as err:
                raise DatabaseAccessError from err
            else:
                return dbquery
        else:
            try:
                dbquery = db.selectBy(self.connection,
                                      **kwargs)
            except SQLObjectNotFound:
                raise DatabaseReadError
            except Exception as err:
                raise DatabaseAccessError from err
            else:
                return dbquery

    def __write_db(self,
                   table: str,
                   **kwargs) -> SQLObject:
        db = getattr(models, table)
        try:
            dbquery = db(**kwargs)
        except (Exception, SQLObjectIntegrityError) as err:
            raise DatabaseWriteError from err
        else:
            return dbquery

    def get_all_user(self) -> SelectResults:
        return self.__read_db(table="UserConfig",
                              get_one=False)

    def get_user_by_uuid(self,
                         uuid: str) -> SQLObject:
        return self.__read_db(table="UserConfig",
                              get_one=True,
                              uuid=uuid)

    def get_user_by_login(self,
                          login: str) -> SQLObject:
        return self.__read_db(table="UserConfig",
                              get_one=True,
                              login=login)

    def get_user_by_login_and_password(self,
                                       login: str,
                                       password: str) -> SQLObject:
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
                 email: str = None,
                 avatar: bytes = None,
                 bio: str = None,
                 salt: bytes = None,
                 key: bytes = None) -> SQLObject:
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
                    email: str = None,
                    avatar: bytes = None,
                    bio: str = None,
                    key: bytes = None,
                    salt: bytes = None) -> str:
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
        return self.__read_db(table="Message",
                              get_one=False)

    def get_message_by_uuid(self,
                            uuid: str) -> SQLObject:
        return self.__read_db(table="Message",
                              get_one=True,
                              uuid=uuid)

    def get_message_by_text(self,
                            text: str) -> SelectResults:
        return self.__read_db(table="Message",
                              get_one=False,
                              text=text)

    def get_message_by_exact_time(self,
                                  time: int) -> SelectResults:
        return models.Message.select(models.Message.q.time == time)

    def get_message_by_less_time(self,
                                 time: int) -> SelectResults:
        return models.Message.select(models.Message.q.time <= time)

    def get_message_by_more_time(self,
                                 time: int) -> SelectResults:
        return models.Message.select(models.Message.q.time >= time)

    def get_message_by_more_time_and_flow(self,
                                          flow_uuid: str,
                                          time: int) -> SelectResults:
        flow = self.__read_db(table="Flow",
                              get_one=True,
                              uuid=flow_uuid)
        return models.Message.select(
            AND(models.Message.q.flow == flow,
                models.Message.q.time >= time))

    def get_message_by_less_time_and_flow(self,
                                          flow_uuid: str,
                                          time: int) -> SelectResults:
        flow = self.__read_db(table="Flow",
                              get_one=True,
                              uuid=flow_uuid)
        return models.Message.select(
            AND(models.Message.q.flow == flow,
                models.Message.q.time <= time))

    def get_message_by_exact_time_and_flow(self,
                                           flow_uuid: str,
                                           time: int) -> SelectResults:
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
        return self.__read_db(table="Flow",
                              get_one=False)

    def get_flow_by_uuid(self,
                         uuid: str) -> SQLObject:
        return self.__read_db(table="Flow",
                              get_one=True,
                              uuid=uuid)

    def get_flow_by_title(self,
                          title: str) -> SelectResults:
        return self.__read_db(table="Flow",
                              get_one=False,
                              title=title)

    def get_flow_by_more_time(self,
                              time: int) -> SelectResults:
        return models.Flow.select(models.Flow.q.time_created >= time)

    def get_flow_by_less_time(self,
                              time: int) -> SelectResults:
        return models.Flow.select(models.Flow.q.time_created <= time)

    def get_flow_by_exact_time(self,
                               time: int) -> SelectResults:
        return models.Flow.select(models.Flow.q.time_created == time)

    def add_flow(self,
                 uuid: str,
                 users: list | tuple,
                 time_created: int = None,
                 flow_type: str = None,
                 title: str = None,
                 info: str = None,
                 owner: str = None) -> SQLObject:
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

    def table_count(self) -> Type[Tuple]:
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
        return self.__read_db(table="Admin",
                              get_one=False)

    def get_admin_by_name(self,
                          username: str) -> SQLObject:
        return self.__read_db(table="Admin",
                              get_one=True,
                              username=username)

    def add_admin(self,
                  username: str,
                  hash_password: str) -> SQLObject:
        return self.__write_db(table="Admin",
                               username=username,
                               hash_password=hash_password)
