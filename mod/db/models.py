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
        uuid (str, required, unique)
        login (str, required)
        password (str, required)
        hash_password (str, optional): default None
        username (str, optional): default None
        is_bot (bool, optional): default False
        auth_id (str, optional): default None
        email (str, optional): default None
        avatar (str, optional): default None
        bio (str, optional): default None
        salt (str, optional): default None
        key (str, optional): default None

    Returns:
        None
    """
    uuid = orm.StringCol(notNone=True, unique=True)
    login = orm.StringCol(notNone=True)
    password = orm.StringCol(notNone=True)
    hash_password = orm.StringCol(default=None)
    username = orm.StringCol(default=None)
    is_bot = orm.BoolCol(default=False)
    auth_id = orm.StringCol(default=None)
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
        uuid (str, required, unique)
        time_created (int, optional): default None
        flow_type (str, optional): default None
        title (str, optional): default None
        info (str, optional): default None

    Returns:
        None
    """
    uuid = orm.StringCol(notNone=True, unique=True)
    time_created = orm.IntCol(default=None)
    flow_type = orm.StringCol(default=None)
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
        uuid (str, required, unique):
        text (str, optional): default None
        time (int, optional): default None
        file_picture (byte, optional): default None
        file_video (byte, optional): default None
        file_audio (byte, optional): default None
        file_document (byte, optional): default None
        emoji (str, optional): default None
        edited_time (int, optional): default None
        edited_status (bool, optional): default False

    Returns:
        None
    """
    uuid = orm.StringCol(notNone=True, unique=True)
    text = orm.StringCol(default=None)
    time = orm.IntCol(default=None)
    file_picture = orm.BLOBCol(default=None)
    file_video = orm.BLOBCol(default=None)
    file_audio = orm.BLOBCol(default=None)
    file_document = orm.BLOBCol(default=None)
    emoji = orm.BLOBCol(default=None)
    edited_time = orm.IntCol(default=None)
    edited_status = orm.BoolCol(default=False)
    # Connection to UserConfig and Flow table
    user = orm.ForeignKey('UserConfig')
    flow = orm.ForeignKey('Flow')


class Admin(orm.SQLObject):
    """Generates a Admin table containing information
        about users with administrators role.

        Args:
            username (str, required, unique)
            hash_password (str, required)

        Returns:
            None
        """
    username = orm.StringCol(notNone=True, unique=True)
    hash_password = orm.StringCol(notNone=True)
