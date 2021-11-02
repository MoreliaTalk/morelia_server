"""
    Copyright (c) 2020 - present NekrodNIK, Stepan Skriabin, rus-ai and other.
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
from collections import namedtuple
import configparser
import inspect
import sys

import sqlobject as orm
from sqlobject import AND
from sqlobject.main import SQLObjectIntegrityError, SQLObjectNotFound
from sqlobject.main import SelectResults

from mod import models

# ************** Read "config.ini" ********************
config = configparser.ConfigParser()
config.read('config.ini')
database = config["DATABASE"]
# ************** END **********************************


class ReadDatabaseError(SQLObjectNotFound):
    #
    pass


class AnotherError(Exception):
    #
    pass


class WriteDatabaseError(SQLObjectNotFound):
    #
    pass


class WriteDatabaseError2(SQLObjectIntegrityError):
    #
    pass


class DbHandler:
    def __init__(self,
                 uri: str = database.get("uri"),
                 debug: bool = False,
                 logger: str = None,
                 loglevel: str = None) -> None:
        self._uri = uri
        self._debug = "0"

        if logger is None:
            self._logger = logger

        if loglevel in ["debug",
                        "info",
                        "warning",
                        "error",
                        "critical",
                        "exception"]:
            self._loglevel = loglevel
        else:
            self._loglevel = ""

        if debug:
            self._debug = "1"

        self._connection = orm.connectionForURI(self._uri,
                                                debug=self._debug,
                                                logger=self._logger,
                                                loglevel=self._loglevel)
        orm.sqlhub.processConnection = self._connection

    def __str__(self):
        return f"Connect to database: {self.uri}"

    def __repr__(self):
        return f"{self.__class__.__name__} at uri: {self.uri}"

    @staticmethod
    def __search_db_in_models(path: str = 'mod.models') -> tuple:
        classes = [cls_name for cls_name, cls_obj
                   in inspect.getmembers(sys.modules[path])
                   if inspect.isclass(cls_obj)]
        return tuple(classes)

    def create(self) -> None:
        # looking for all Classes listed in models.py
        for item in self.__search_db_in_models():
            # Create tables in database for each class
            # that is located in models module
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        return "Ok"

    def delete(self) -> None:
        # looking for all Classes listed in models.py
        for item in self.__search_db_in_models():
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True, dropJoinTables=True, cascade=True)
        return "Ok"

    @property
    def debug(self) -> bool | None:
        match self._debug:
            case "0":
                return False
            case "1":
                return True
            case _:
                return None

    @debug.setter
    def debug(self,
              value: bool = False) -> None:
        self._debug = "0"
        if value:
            self._debug = "1"
        self._connection = orm.connectionForURI(self._uri,
                                                debug=self._debug)
        orm.sqlhub.processConnection = self._connection

    @staticmethod
    def __read_userconfig(get_one: bool,
                          **kwargs) -> SelectResults:
        if get_one:
            try:
                dbquery = models.UserConfig.selectBy(**kwargs).getOne()
            except SQLObjectNotFound as error:
                raise ReadDatabaseError("") from error
            except Exception as error:
                raise AnotherError("") from error
            else:
                return dbquery
        else:
            try:
                dbquery = models.UserConfig.selectBy(**kwargs)
            except SQLObjectNotFound as error:
                raise ReadDatabaseError("") from error
            except Exception as error:
                raise AnotherError("") from error
            else:
                return dbquery

    @staticmethod
    def __write_userconfig(**kwargs) -> None:
        try:
            models.UserConfig(**kwargs)
        except SQLObjectNotFound as error:
            raise WriteDatabaseError("") from error
        except SQLObjectIntegrityError as error:
            raise WriteDatabaseError2("") from error
        except Exception as error:
            raise AnotherError("") from error

    @staticmethod
    def __read_flow(get_one: bool,
                    **kwargs) -> SelectResults:
        if get_one:
            try:
                dbquery = models.Flow.selectBy(**kwargs).getOne()
            except SQLObjectNotFound as error:
                raise ReadDatabaseError("") from error
            except Exception as error:
                raise AnotherError("") from error
            else:
                return dbquery
        else:
            try:
                dbquery = models.Flow.selectBy(**kwargs)
            except SQLObjectNotFound as error:
                raise ReadDatabaseError("") from error
            except Exception as error:
                raise AnotherError("") from error
            else:
                return dbquery

    @staticmethod
    def __write_flow(**kwargs) -> None:
        try:
            models.Flow(**kwargs)
        except SQLObjectNotFound as error:
            raise WriteDatabaseError("") from error
        except SQLObjectIntegrityError as error:
            raise WriteDatabaseError2("") from error
        except Exception as error:
            raise AnotherError("") from error

    @staticmethod
    def __read_message(get_one: bool,
                       **kwargs) -> SelectResults:
        if get_one:
            try:
                dbquery = models.Message.selectBy(**kwargs).getOne()
            except SQLObjectNotFound as error:
                raise ReadDatabaseError("") from error
            except Exception as error:
                raise AnotherError("") from error
            else:
                return dbquery
        else:
            try:
                dbquery = models.Message.selectBy(**kwargs)
            except SQLObjectNotFound as error:
                raise ReadDatabaseError("") from error
            except Exception as error:
                raise AnotherError("") from error
            else:
                return dbquery

    @staticmethod
    def __write_message(**kwargs) -> None:
        try:
            models.Message(**kwargs)
        except SQLObjectNotFound as error:
            raise WriteDatabaseError("") from error
        except SQLObjectIntegrityError as error:
            raise WriteDatabaseError2("") from error
        except Exception as error:
            raise AnotherError("") from error

    @staticmethod
    def __read_admin(get_one: bool,
                     **kwargs) -> SelectResults:
        if get_one:
            try:
                dbquery = models.Admin.selectBy(**kwargs).getOne()
            except SQLObjectNotFound as error:
                raise ReadDatabaseError("") from error
            except Exception as error:
                raise AnotherError("") from error
            else:
                return dbquery
        else:
            try:
                dbquery = models.Admin.selectBy(**kwargs)
            except SQLObjectNotFound as error:
                raise ReadDatabaseError("") from error
            except Exception as error:
                raise AnotherError("") from error
            else:
                return dbquery

    @staticmethod
    def __write_admin(**kwargs) -> None:
        try:
            models.Admin(**kwargs)
        except SQLObjectNotFound as error:
            raise WriteDatabaseError("") from error
        except SQLObjectIntegrityError as error:
            raise WriteDatabaseError2("") from error
        except Exception as error:
            raise AnotherError("") from error

    def get_all_user(self) -> SelectResults:
        return self.__read_userconfig(get_one=False)

    def get_user_by_uuid(self,
                         uuid: str) -> SelectResults:
        return self.__read_userconfig(get_one=True,
                                      uuid=uuid)

    def get_user_by_login(self,
                          login: str) -> SelectResults:
        return self.__read_userconfig(get_one=True,
                                      login=login)

    def get_user_by_login_and_password(self,
                                       login: str,
                                       password: str) -> SelectResults:
        return self.__read_userconfig(get_one=True,
                                      login=login,
                                      password=password)

    def add_new_user(self,
                     uuid: str,
                     login: str,
                     password: str,
                     hash_password: str,
                     username: str,
                     salt: str,
                     key: str,
                     email: str = None,
                     auth_id: str = None) -> None:
        return self.__write_userconfig(uuid=uuid,
                                       login=login,
                                       password=password,
                                       hashPassword=hash_password,
                                       username=username,
                                       isBot=False,
                                       authId=auth_id,
                                       email=email,
                                       avatar=None,
                                       bio=None,
                                       salt=salt,
                                       key=key)

    def update_user_info(self,
                         uuid: str,
                         hash_password: str = None,
                         username: str = None,
                         is_bot: bool = False,
                         auth_id: str = None,
                         email: str = None,
                         avatar: bytes = None,
                         bio: str = None) -> None:
        dbquery = self.__read_userconfig(get_one=True,
                                         uuid=uuid)
        if hash_password:
            dbquery.hashPassword = hash_password
        if username:
            dbquery.username = username
        if is_bot:
            dbquery.isBot = is_bot
        if auth_id:
            dbquery.authId = auth_id
        if email:
            dbquery.email = email
        if avatar:
            dbquery.avatar = avatar
        if bio:
            dbquery.bio = bio

    def get_all_message(self) -> SelectResults:
        return self.__read_message(get_one=False)

    def get_message_by_uuid(self,
                            uuid: str) -> SelectResults:
        return self.__read_message(get_one=True,
                                   uuid=uuid)

    def get_message_by_date(self,
                            time: int) -> SelectResults:
        return models.Flow.select(models.Message.q.time >= time)

    def get_message_by_more_date_and_flow(self,
                                          flow_uuid: str,
                                          time: int) -> SelectResults:
        flow = self.__read_flow(uuid=flow_uuid)
        return models.Message.select(
            AND(models.Message.q.flow == flow,
                models.Message.q.time >= time))

    def get_message_by_less_date_and_flow(self,
                                          flow_uuid: str,
                                          time: int) -> SelectResults:
        flow = self.__read_flow(uuid=flow_uuid)
        return models.Message.select(
            AND(models.Message.q.flow == flow,
                models.Message.q.time <= time))

    def get_message_by_exact_date_and_flow(self,
                                           flow_uuid: str,
                                           time: int) -> SelectResults:
        flow = self.__read_flow(uuid=flow_uuid)
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
                    emoji: bytes = None) -> None:
        flow = self.__read_flow(get_one=True,
                                uuid=flow_uuid)
        user = self.__read_userconfig(get_one=True,
                                      uuid=user_uuid)
        return self.__write_message(uuid=message_uuid,
                                    text=text,
                                    time=time,
                                    filePicture=picture,
                                    fileVideo=video,
                                    fileAudio=audio,
                                    fileDocument=document,
                                    emoji=emoji,
                                    editedTime=None,
                                    editedStatus=False,
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
                       edited_status: bool = False) -> None:
        dbquery = self.__read_message(get_one=True,
                                      uuid=uuid)
        if text:
            dbquery.text = text
        if text:
            dbquery.filePicture = picture
        if text:
            dbquery.fileVideo = video
        if text:
            dbquery.fileAudio = audio
        if text:
            dbquery.fileDocument = document
        if text:
            dbquery.emoji = emoji
        if text:
            dbquery.editedTime = edited_time
        if text:
            dbquery.editedStatus = edited_status

    def get_all_flow(self) -> SelectResults:
        return self.__read_flow(get_one=False)

    def get_flow_by_uuid(self,
                         uuid: str) -> SelectResults:
        return self.__read_flow(get_one=True,
                                uuid=uuid)

    def get_flow_by_more_date(self,
                              time: int) -> SelectResults:
        return models.Flow.select(models.Flow.q.timeCreated >= time)

    def get_flow_by_less_date(self,
                              time: int) -> SelectResults:
        return models.Flow.select(models.Flow.q.timeCreated <= time)

    def get_flow_by_exact_date(self,
                               time: int) -> SelectResults:
        return models.Flow.select(models.Flow.q.timeCreated == time)

    def add_flow(self,
                 uuid: str,
                 time_created: int,
                 flow_type: str,
                 title: str,
                 info: str,
                 owner: str,
                 users: list | tuple = None) -> None:
        dbquery = self.__write_flow(uuid=uuid,
                                    timeCreated=time_created,
                                    flowType=flow_type,
                                    title=title,
                                    info=info,
                                    owner=owner)
        for user_uuid in users:
            user = self.__read_userconfig(get_one=True,
                                          uuid=user_uuid)
            dbquery.addUserConfig(user)
        return

    def update_flow(self,
                    uuid: str,
                    flow_type: str,
                    title: str,
                    info: str,
                    owner: str) -> None:
        dbquery = self.__read_flow(get_one=True,
                                   uuid=uuid)
        if flow_type:
            dbquery.flowType = flow_type
        if flow_type:
            dbquery.title = title
        if flow_type:
            dbquery.info = info
        if flow_type:
            dbquery.owner = owner

    def table_count(self) -> namedtuple:
        TableCount = namedtuple('TableCount', ["user_count",
                                               "flow_count",
                                               "message_count"])
        user = self.__read_userconfig(get_one=False)
        flow = self.__read_flow(get_one=False)
        message = self.__read_message(get_one=False)
        result = TableCount(user.count(),
                            flow.count(),
                            message.count())
        return result

    def get_admin(self,
                  username: str) -> SelectResults:
        return self.__read_admin(get_one=True,
                                 username=username)

    def add_admin(self,
                  username: str,
                  hash_password: str) -> None:
        return self.__write_admin(username=username,
                                  hashPassword=hash_password)
