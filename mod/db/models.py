"""
Copyright (c) 2020 - present MoreliaTalk team and other.
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
    """
    Table containing data about user and his settings.

    Args:
        uuid (str, required, unique): unique user id which automated
                                      generating server
        login (str, required): name for authentication on server
        password (str, required): password for authentication on server
        hash_password (str, optional): hash-function generated from user
                                       password
        username (str, optional): name for added in information about user
        is_bot (bool, optional): True if user not human
        auth_id (str, optional): authentication token
        email (str, optional): user email for added in information about user
        avatar (str, optional): user image for added in information about user
        bio (str, optional): text for added in information about user
        salt (str, optional): added in password string for create hash_password
        key (str, optional): added in password string for create hash_password
    """

    uuid = orm.StringCol(notNone=True, unique=True)
    login = orm.StringCol(notNone=True)
    password = orm.StringCol(notNone=True)
    hash_password = orm.StringCol(default=None)
    username = orm.StringCol(default=None)
    is_bot = orm.BoolCol(default=False)
    auth_id = orm.StringCol(default=None)
    token_ttl = orm.IntCol(default=None)
    email = orm.StringCol(default=None)
    avatar = orm.BLOBCol(default=None)
    bio = orm.StringCol(default=None)
    salt = orm.BLOBCol(default=None)
    key = orm.BLOBCol(default=None)
    # Connection to Message and Flow table
    messages = orm.MultipleJoin('Message')
    flows = orm.RelatedJoin('Flow')


class Flow(orm.SQLObject):
    """
    Flow table containing information about threads and their types.

    Args:
        uuid (str, required, unique): unique flow id which automated
                                      generating server
        time_created (int, optional): data and time when flow is created
        flow_type (str, optional): which contains chat, channel, group
        title (str, optional): name added in public information about flow
        info (str, optional): text added in public information about flow
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
    """
    Message table containing information about user messages.

    Args:
        uuid (str, required, unique): unique flow id which automated
                                      generating server
        text (str, optional): contains message text
        time (int, optional): time when message is created
        file_picture (byte, optional): contains appended image
        file_video (byte, optional): contains appended video
        file_audio (byte, optional): contains appended audio
        file_document (byte, optional): contains appended document
        emoji (str, optional): contains appended image/emoji
        edited_time (int, optional): time when user last time is corrected his
                                     message
        edited_status (bool, optional): True if user corrected his message
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
    """
    Admin table containing information about users with administrators role.

    Args:
        username (str, required, unique): name user which granted administrator
                                          rights
        hash_password (str, required): hash-function generated from
                                       administrator password
    """

    username = orm.StringCol(notNone=True, unique=True)
    hash_password = orm.StringCol(notNone=True)
