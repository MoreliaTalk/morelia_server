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
import sqlobject as orm


class UserConfig(orm.SQLObject):
    """Generates a table containing data
    about user and his settings.

    Args:
        uuid (str, required):
        login (str, required):
        password (str, required):
        hash_password (str, optional)
        username (str, optional):
        isBot (bool, optional): default False
        authId (str, optional):
        email (str, optional):
        avatar (str, optional):
        bio (str, optional):
        salt (str, optional):
        key (str, optional):

    Returns:
        None
    """
    uuid = orm.StringCol(notNone=True, unique=True)
    login = orm.StringCol(notNone=True)
    password = orm.StringCol(notNone=True)
    hashPassword = orm.StringCol(default=None)
    username = orm.StringCol(default=None)
    isBot = orm.BoolCol(default=False)
    authId = orm.StringCol(default=None)
    email = orm.StringCol(default=None)
    avatar = orm.BLOBCol(default=None)
    bio = orm.StringCol(default=None)
    salt = orm.BLOBCol(default=None)
    key = orm.BLOBCol(default=None)
    # Connection to Message and Flow table
    messages = orm.MultipleJoin('Message')
    flows = orm.RelatedJoin('Flow')


class Flow(orm.SQLObject):
    """Generates a Flow table containing information
    about threads and their types (chat, channel, group).

    Args:
        uuid (str, required):
        timeCreated (int, optional):
        flowType (str, optional):
        title (str, optional):
        info (str, optional):

    Returns:
        None
    """
    uuid = orm.StringCol(notNone=True, unique=True)
    timeCreated = orm.IntCol(default=None)
    flowType = orm.StringCol(default=None)
    title = orm.StringCol(default=None)
    info = orm.StringCol(default=None)
    owner = orm.StringCol(default=None)
    # Connection to the Message and UserConfig table
    messages = orm.MultipleJoin('Message')
    users = orm.RelatedJoin('UserConfig')


class Message(orm.SQLObject):
    """Generates a Message table containing information
    about user messages.

    Args:
        uuid (str, required):
        text (str, optional):
        time (int, optional):
        filePicture (byte, optional):
        fileVideo (byte, optional):
        fileAudio (byte, optional):
        fileDocument (byte, optional):
        emoji (str, optional):
        editedTime (int, optional):
        editedStatus (bool, optional):

    Returns:
        None
    """
    uuid = orm.StringCol(notNone=True, unique=True)
    text = orm.StringCol(default=None)
    time = orm.IntCol(default=None)
    filePicture = orm.BLOBCol(default=None)
    fileVideo = orm.BLOBCol(default=None)
    fileAudio = orm.BLOBCol(default=None)
    fileDocument = orm.BLOBCol(default=None)
    emoji = orm.BLOBCol(default=None)
    editedTime = orm.IntCol(default=None)
    editedStatus = orm.BoolCol(default=False)
    # Connection to UserConfig and Flow table
    user = orm.ForeignKey('UserConfig')
    flow = orm.ForeignKey('Flow')


class Admin(orm.SQLObject):
    username = orm.StringCol(notNone=True, unique=True)
    hashPassword = orm.StringCol(notNone=True)
