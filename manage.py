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

import asyncio
from functools import wraps
import os
from pathlib import Path
import random
from time import time
from typing import Callable
from uuid import uuid4

import click
from sqlobject import SQLObjectNotFound
import uvicorn
from websockets import client as ws_client
from websockets import exceptions as ws_exceptions

from mod.config.handler import BackupNotFoundError
from mod.config.handler import ConfigHandler
from mod.db.dbhandler import DatabaseAccessError
from mod.db.dbhandler import DatabaseReadError
from mod.db.dbhandler import DatabaseWriteError
from mod.db.dbhandler import DBHandler
from mod.lib import Hash
from mod.protocol.api import BaseUser
from mod.protocol.api import BaseVersion
from mod.protocol.api import DataRequest
from mod.protocol.api import FlowRequest
from mod.protocol.api import Request
from server import MoreliaServer

VERSION = 'v0.3'

DEFAULT_CONFIG = 'config.ini'

DEFAULT_DB = 'db_sqlite.db'

SYMBOLS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'


async def connect_ws_and_send(message: Request,
                              address: str) -> None:
    """
    Connect and send message to address.

    Args:
        message: message for send
        address(str): server address
    """
    try:
        ws = await ws_client.connect(address)
    except ConnectionRefusedError:
        click.echo("Unable to connect to the server, please check the server")
    else:
        await ws.send(message.json())
        try:
            response = await ws.recv()
        except ws_exceptions.ConnectionClosedError as error:
            click.echo(f"Server disconnected not normal, error: {error}")
        else:
            click.echo(response)
            await ws.close(1000)


def click_async(func: Callable):
    """
    Wrapper to call the click function asynchronously.

    Args:
        func: function

    Returns:
        (wrapper)
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


def create_table() -> None:
    """
    Creates a database file and fills it with empty tables.
    """

    config = ConfigHandler()
    config_options = config.read()
    db = DBHandler(uri=config_options.database.url)
    db.create_table()


def create_administrator(username: str,
                         password: str) -> None:
    """
    Creates an administrator account to manage the server.

    Args:
        username: name for new administrator user
        password: password for new administrator user
    """

    config = ConfigHandler()
    config_read = config.read()
    db = DBHandler(uri=config_read.database.url)
    user_uuid = str(uuid4().int)
    db.add_admin(username=username,
                 hash_password=Hash(password, user_uuid).password_hash())


@click.group(name="Main group for all options.",
             help="MoreliaTalkServer manager")
@click.version_option(version=VERSION,
                      package_name="MoreliaTalkServer")
@click.help_option()
def cli() -> None:
    """
    Morelia Talk server manager.

    It's main tool for working with the MoreliaTalk server,
    allowing you to start and configure server.
    """


@cli.group("create",
           help="Tools for creating object in database.")
@click.option("--uri",
              default="sqlite:db_sqlite.db",
              show_default=True,
              help="Connection to database.")
@click.pass_context
def create(context: click.Context,
           uri: str) -> None:
    """
    Tools for creating object in database.

    Args:
        context: click call context
        uri: Connection to database, like: sqlite:db_sqlite.db
    """

    context.ensure_object(dict)
    context.obj['uri'] = uri


@create.command("db",
                help="Create all table with all data")
@click.pass_context
def create_db(context: click.Context) -> None:
    """
    Create database, and create all table which contain in models.
    """

    db = DBHandler(context.obj["uri"])
    try:
        db.create_table()
    except (DatabaseReadError,
            DatabaseAccessError,
            DatabaseWriteError) as err:
        click.echo(f"The database is unavailable, table not created. {err}")
    else:
        click.echo("Database is created.")


@create.command("user",
                help="Creates a user in the database, \
                if login and password are empty, \
                then generates them randomly")
@click.option("--login",
              type=str,
              default="".join(random.sample(SYMBOLS, 6)),
              help="New user login name.")
@click.option("--username",
              type=str,
              default="User",
              show_default=True,
              help="New user name.")
@click.option("--password",
              type=str,
              default="".join(random.sample(SYMBOLS, 20)),
              help="New user password.")
@click.pass_context
def create_user(context: click.Context,
                login: str,
                username: str,
                password: str) -> None:
    """
    Create user in database.

    Args:
        context: click call context
        login: user login
        username: username
        password: user password
    """

    db = DBHandler(context.obj["uri"])
    try:
        db.create_table()
    except DatabaseWriteError as error:
        click.echo(f"Failed to create database. Error text: {error}")
        return None

    user_uuid = str(uuid4().int)
    try:
        db.add_user(uuid=user_uuid,
                    login=login,
                    password=password,
                    hash_password=Hash(password, user_uuid).password_hash(),
                    username=username,
                    salt=b"salt",
                    key=b"key")
    except Exception as err:
        click.echo(f"{err}")
    else:
        click.echo(f"User with name={username}, login={login}, ")
        click.echo(f"and password={password} is created")


@create.command("flow",
                help="Create flow type group in database")
@click.option("--login",
              type=str,
              help="Use login which you specified when create user")
@click.pass_context
def create_flow(context: click.Context,
                login: str) -> None:
    """
    Creating and adding test flow (group) to database.

    Args:
        context: click call context.
        login: use login which you specified when create user.
    """

    db = DBHandler(context.obj["uri"])
    try:
        db.create_table()
    except DatabaseWriteError as error:
        click.echo(f"Failed to create database. Error text: {error}")
        return None

    try:
        user = db.get_user_by_login(login=login)
    except (DatabaseReadError,
            DatabaseAccessError,
            DatabaseWriteError) as error:
        click.echo(f'Failed to create a flow. Error text: {error}')
    else:
        new_flow = db.add_flow(uuid=str(uuid4().int),
                               users=[user.uuid],
                               time_created=int(time()),
                               flow_type="group",
                               title="Test",
                               info="Test flow",
                               owner=user.uuid)
        new_flow.addUserConfig(user)
        click.echo("Flow created.")


@create.command("admin",
                help="Create user for admin panel")
@click.option("--username",
              type=str,
              prompt=True,
              help="Name for administrator user.")
@click.option("--password",
              type=str,
              prompt=True,
              hide_input=True,
              help="New password for administrator user.")
@click.pass_context
def create_admin(context: click.Context,
                 username: str,
                 password: str) -> None:
    """
    Create Admin user to management server with admin panel.

    Args:
        context: click call context
        username: name of admin user
        password: password of admin user
    """

    db = DBHandler(context.obj["uri"])
    try:
        db.create_table()
    except DatabaseWriteError as error:
        click.echo(f"Failed to create database. Error text: {error}")
        return None

    generator = Hash(password,
                     str(uuid4().int),
                     key=b"key",
                     salt=b"salt")
    try:
        db.add_admin(username=username,
                     hash_password=generator.password_hash())
    except (DatabaseReadError,
            DatabaseAccessError,
            DatabaseWriteError) as error:
        click.echo(f'Failed to create a flow. Error text: {error}')
    else:
        click.echo("Admin created.")
        click.echo(f"User name={username}, password={password}")


@cli.group("delete",
           help="Tools for deleting object in database.")
@click.option("--uri",
              default="sqlite:db_sqlite.db",
              show_default=True,
              help="Connection to database.")
@click.pass_context
def delete(context: click.Context,
           uri: str) -> None:
    """
    Tools for deleting object in database.

    Args:
        context: click call context
        uri: Connection to database, like: sqlite:db_sqlite.db
    """

    context.ensure_object(dict)
    context.obj['uri'] = uri


@delete.command("db",
                help="Delete all table with all data")
@click.pass_context
def delete_db(context: click.Context) -> None:
    """
    Delete all tables which contains data.

    This function not delete database file.

    Args:
        context: click call context
    """

    db = DBHandler(context.obj["uri"])
    try:
        db.delete_table()
    except (DatabaseReadError,
            DatabaseAccessError,
            DatabaseWriteError) as err:
        click.echo(f"The database is unavailable, table not deleted. {err}")
    else:
        click.echo("All table is deleted.")


@cli.group("client",
           help="Mini-client for send message to the MoreliaTalk server.")
def client() -> None:
    """
    Mini-client for send message to the MoreliaTalk server.
    """


@client.command("send",
                help="Send message to server used API method name.")
@click.option("--login",
              type=str,
              help="User login.")
@click.option("--username",
              type=str,
              help="User name.")
@click.option("--password",
              type=str,
              help="User password.")
@click.option("--user-uuid",
              type=str,
              help="User unique ID.")
@click.option("--user-auth-id",
              type=str,
              help="User authentication ID.")
@click.option("--flow-uuid",
              type=str,
              help="Flow unique ID.")
@click.option("--type",
              "type_",
              type=click.Choice(("register_user",
                                 "get_update",
                                 "send_message",
                                 "all_messages",
                                 "add_flow",
                                 "all_flow",
                                 "user_info",
                                 "authentication",
                                 "ping_pong")),
              default="send_message",
              show_default=True,
              help="MTP protocol API method name.")
@click.option("--address",
              type=str,
              default="ws://127.0.0.1:8080/ws",
              show_default=True,
              help="Server address and port.")
@click_async
async def send(login: str,
               username: str,
               password: str,
               user_uuid: str,
               flow_uuid: str,
               user_auth_id: str,
               type_: str,
               address: str) -> None:
    """
    Connect and send message protocol method.

    Args:
        login: user login.
        username: user name.
        password: user password.
        user_uuid: user uuid.
        flow_uuid: flow uuid.
        user_auth_id: user authentication ID.
        type_: name of API method.
        address: server address.
    """

    message = Request(type=type_,
                      jsonapi=BaseVersion(version="1.0"))
    message.data = DataRequest()
    message.data.user = []
    message.data.user.append(BaseUser())
    message.parse_file(Path(Path(__file__).parent,
                            "tests",
                            "fixtures",
                            "".join((type_, ".json"))))
    match type_:
        case ("register_user"):
            message.data.user[0].username = username
            message.data.user[0].password = password
        case ("get_update",
              "add_flow",
              "all_flow",
              "ping_pong",
              "user_info"):
            message.data.user[0].uuid = user_uuid
            message.data.user[0].auth_id = user_auth_id
        case ("all_message", "send_message"):
            message.data.flow = []
            message.data.flow.append(FlowRequest())
            message.data.flow[0].uuid = flow_uuid
            message.data.user[0].uuid = user_uuid
            message.data.user[0].auth_id = user_auth_id
        case ("authentication"):
            message.data.user[0].password = password
            message.data.user[0].login = login

    await connect_ws_and_send(message, address)


@cli.group("run",
           help="Tools for running server in production or developing mode.")
def run() -> None:
    """
    Tools for running server in production or developing mode.
    """


@run.command("init")
@click.option("--username",
              type=str,
              prompt=True,
              help="Name for new user.")
@click.option("--password",
              type=str,
              prompt=True,
              hide_input=True,
              help="Password for new user.")
def init(username: str,
         password: str) -> None:
    """
    Preparing the MoreliaTalk server for work.

    This command will copy config.ini from example_config.ini,
    create a database and an administrator account.

    Args:
        username: name for new administrator user
        password: password for new administrator user
    """

    try:
        create_table()
    except SQLObjectNotFound:
        click.echo("Database file not found, or ")
        click.echo("no write access rights in the current directory.")
    except Exception as err:
        click.echo(f"Database =>x Bad. An unknown error occurred. {err}")
        return
    else:
        click.echo("Database => Ok.")

    try:
        create_administrator(username,
                             password)
    except DatabaseWriteError:
        click.echo("Database file not found, or ")
        click.echo("no write access rights in the current directory.")
    except Exception as err:
        click.echo(f"Create admin =>x Bad. An unknown error occurred. {err}")
    else:
        click.echo("Create admin => Ok.")
        click.echo(f"User name={username} is created")
        click.echo("<=====================================================>")
        click.echo("For run server in normal mode: ./manage.py run server")
        click.echo("For run server in develop mode: ./manage.py run devserver")


@run.command("conf_restore",
             help="Restore default configuration or backup")
@click.option("--backup/--no-backup",
              type=bool,
              default=False,
              help="Backup current config")
@click.option("--source", type=str, default=None, help="path to backup file")
def conf_restore(backup: bool, source: str | None):
    """
    Restore configuration default config file or backup.

    Args:
        backup(bool): backup current config file
        source(str | None): path to backup file for restore,
        if None, restore default config
    """
    config = ConfigHandler(log=False)

    if backup:
        config.backup()

    if source:
        try:
            config.restore(source)
        except BackupNotFoundError:
            click.echo(f"Backup from {source} is not found")
        else:
            click.echo(f"Successful restore config from {source}")
    else:
        config.restore()
        click.echo("Successful restore default config")


@run.command("conf_backup",
             help="Backup current config")
@click.option("--backup-name",
              type=str)
def conf_backup(backup_name: str | None):
    """
    Backup current config file.

    Args:
        backup_name(str | None): name for new backup
    """
    ConfigHandler(log=False).backup(backup_name)
    click.echo("Successful backup current config")


@run.command("devserver",
             help="Run server in debug (developing) mode.")
@click.option("--host",
              type=str,
              default="127.0.0.1",
              show_default=True,
              help="IP or DNS name for running server")
@click.option("--port",
              type=int,
              default=8080,
              show_default=True,
              help="IP port for running server")
@click.option("--log-level",
              type=click.Choice(("critical",
                                 "error",
                                 "warning",
                                 "info",
                                 "debug",
                                 "trace")),
              default="debug",
              show_default=True,
              help="level logs")
@click.option("--use-colors",
              is_flag=True,
              default=True,
              show_default=True,
              help="enable use colors in terminal")
@click.option("--reload",
              is_flag=True,
              default=True,
              show_default=True,
              help="enable hot reloaded")
def devserver(host: str,
              port: int,
              log_level: str,
              use_colors: bool,
              reload: bool) -> None:
    """
    Run server in debug (developing) mode.

    Args:
        host: IP or DNS name for running server
        port: IP port for running server
        log_level: level logs
        use_colors: enable use colors in terminal
        reload: enable hot reloaded
    """

    uvicorn.run(MoreliaServer().get_starlette_app(),
                host=host,
                port=port,
                http="h11",
                ws="websockets",
                log_level=log_level,
                use_colors=use_colors,
                debug=True,
                reload=reload)

    click.echo(f"Develop server started at address=https//{host}:{port}")


@run.command("server",
             help="Run server in production (normal) mode.")
@click.option("--host",
              type=str,
              default="localhost",
              show_default=True,
              help="IP or DNS name for running server")
@click.option("--port",
              type=int,
              default=8080,
              show_default=True,
              help="IP port for running server")
@click.option("--log-level",
              type=click.Choice(("critical",
                                 "error",
                                 "warning",
                                 "info",
                                 "debug",
                                 "trace")),
              default="error",
              show_default=True,
              help="level logs")
@click.option("--use-colors",
              is_flag=True,
              default=False,
              show_default=True,
              help="enable use colors in terminal")
@click.option("--reload",
              is_flag=True,
              default=False,
              show_default=True,
              help="enable hot reloaded")
def server(host: str,
           port: int,
           log_level: str,
           use_colors: bool,
           reload: bool) -> None:
    """
    Run server in production (normal) mode.

    Args:
        host: IP or DNS name for running server
        port: IP port for running server
        log_level: level logs
        use_colors: enable use colors in terminal
        reload: enable hot reloaded
    """

    click.echo(f"Server started at address=https//{host}:{port}")
    uvicorn.run("server:app",
                host=host,
                port=port,
                http="h11",
                ws="websockets",
                log_level=log_level,
                use_colors=use_colors,
                debug=False,
                reload=reload)


@run.command("clean",
             help="Clean created config and database file.")
@click.option("--config-name",
              type=str,
              show_default=True,
              default=DEFAULT_CONFIG,
              help="name of config file")
@click.option("--db-name",
              type=str,
              show_default=True,
              default=DEFAULT_DB,
              help="name of database file")
@click.confirmation_option(prompt='Are you sure you want to drop file?')
def clean_init(config_name: str,
               db_name: str) -> None:
    """
    Clean created config and database file.

    Args:
        config_name: name of config file.
        db_name: name of database file.
    """

    if Path(config_name).is_file():
        os.remove(config_name)
        click.echo("Config file => deleted.")
    else:
        click.echo("Config file is not found => NOT deleted.")

    if Path(db_name).is_file():
        os.remove(db_name)
        click.echo("Database file => deleted.")
    else:
        click.echo("Database file is not found => NOT deleted.")


if __name__ == "__main__":
    cli()
