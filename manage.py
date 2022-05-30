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

import asyncio
from functools import wraps
from pathlib import Path
import random
from time import process_time
from time import time
from uuid import uuid4

import click
import uvicorn
from websockets import client as ws_client
from websockets import exceptions as ws_exceptions

from mod import lib
from mod.config.config import ConfigHandler
from mod.db.dbhandler import DatabaseAccessError
from mod.db.dbhandler import DatabaseReadError
from mod.db.dbhandler import DatabaseWriteError
from mod.db.dbhandler import DBHandler
from mod.protocol.mtp.api import BaseUser
from mod.protocol.mtp.api import BaseVersion
from mod.protocol.mtp.api import DataRequest
from mod.protocol.mtp.api import Request


VERSION = "v0.3"


config = ConfigHandler()
config_option = config.read()

SYMBOLS_FOR_RANDOM = "abcdefghijklmnopqrstuvwxyz \
                      ABCDEFGHIJKLMNOPQRSTUVWXYZ \
                      1234567890"


async def connect_ws_and_send(message: Request,
                              address: str):
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


def click_async(func):
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


def copy_config():
    pass


def create_table():
    pass


def create_superuser(username):
    click.echo(f"{username}")


@click.group(name="Main group for all options.")
@click.version_option(version=VERSION,
                      package_name="MoreliaTalk server")
@click.help_option()
def cli() -> None:
    """
    Morelia Talk server manager.

    It's main tool for working with the MoreliaTalk server,
    allowing you to start and configure server.
    """


@cli.group("init")
# @click.option("--username",
#               help="Username")
# @click.option("--password",
#               prompt=True,
#               hide_input=True)
def init() -> None:
    """
    Preparing the MoreliaTalk server for work.

    This command will copy config.ini from example_config.ini,
    create a database and an administrator account.
    """
    try:
        copy_config()
    except Exception as err:
        click.echo(f"Error{err}")
        return
    else:
        click.echo("Config => Ok")

    try:
        create_table()
    except Exception as err:
        click.echo(f"ERROR={err}")
        return
    else:
        click.echo("Database => Ok")

    try:
        create_superuser()
    except Exception as err:
        click.echo(f"ERROR={err}")
    else:
        click.echo("User created => Ok")
        # click.echo(f"name={} with password={}")
        click.echo("For run server in normal mode: ./manage.py run server")
        click.echo("For run server in develop mode: ./manage.py run devserver")


@cli.group("db")
@click.pass_context
def db() -> None:
    """
    Tools for creating and managing database.

    """


@cli.group("client")
def client() -> None:
    """
    Mini-client for checking the server.

    """


@cli.group("run")
def run() -> None:
    """
    Tools for running server in production or developing mode.

    """


@run.command("devserver")
@click.option("-h",
              "--host",
              default="localhost")
@click.option("-p",
              "--port",
              default=8080)
@click.option("--log-level",
              default="debug")
@click.option("--use-colors",
              default=True)
@click.option("-r",
              "--reload",
              default=True)
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
        reload: enable hot reload
    """

    uvicorn.run("server:app",
                host=host,
                port=port,
                http="h11",
                ws="websockets",
                log_level=log_level,
                use_colors=use_colors,
                debug=True,
                reload=reload)


@run.command("server")
@click.option("-h",
              "--host",
              default="localhost")
@click.option("-p",
              "--port",
              default=8080)
@click.option("--log-level",
              default="error")
@click.option("--use-colors",
              default=False)
@click.option("-r",
              "--reload",
              default=True)
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
        reload: enable hot reload
    """

    uvicorn.run("server:app",
                host=host,
                port=port,
                http="h11",
                ws="websockets",
                log_level=log_level,
                use_colors=use_colors,
                debug=False,
                reload=reload)


@db.command("create", help="Create all table with all data")
@click.pass_context
def db_create(ctx):
    """
    Create database, and create all table which contain in models.
    """

    start_time = process_time()
    db = DBHandler(ctx.obj["uri"])
    try:
        db.create_table()
    except Exception as err:
        click.echo(f"table not created. Error={err}")
    else:
        click.echo(f"Table is created at: "
                   f"{process_time() - start_time} sec.")


@db.command("delete", help="Delete all table with all data")
@click.pass_context
def db_delete(ctx):
    """
    Delete all tables which contains data.
    This function not delete database file.
    """

    start_time = process_time()
    db = DBHandler(ctx.obj["uri"])
    try:
        db.delete_table()
    except Exception as err:
        click.echo(f"table not created. Error={err}")
    else:
        click.echo(f"Table is deleted at: "
                   f"{process_time() - start_time} sec.")


@db.command("user-create", help="Creates a user in the database, \
                                     if login and password are empty, \
                                     then generates them randomly")
@click.option("-l",
              "--login",
              default="".join(random.sample(SYMBOLS_FOR_RANDOM, 6)))
@click.option("--username", default="User")
@click.option("-p",
              "--password",
              default="".join(random.sample(
                  SYMBOLS_FOR_RANDOM, 20
              )))
@click.pass_context
def create_user(ctx: click.Context,
                login: str,
                username: str,
                password: str):
    """
    Create user in database.

    Args:
        ctx(click.Context): click call context
        login(str): user login
        username(str): username
        password(str): user password
    """

    db = DBHandler(ctx.obj["uri"])
    user_uuid = str(uuid4().int)
    try:
        db.add_user(uuid=user_uuid,
                    login=login,
                    password=password,
                    hash_password=lib.Hash(password, user_uuid).hash_password,
                    username=username,
                    salt=b"salt",
                    key=b"key")
    except DatabaseWriteError as error:
        click.echo(f"Failed to create a user. Error text: {error}")
    else:
        click.echo(f"{username} created, login: {login}, password: {password}")


@db.command("flow-create", help="Create flow type group in database")
@click.option("-l",
              "--login",
              help="Use login which you specified when run user-create")
@click.pass_context
def create_flow(ctx, login: str):
    """
    Creating and adding test flow (group) in database.
    """

    db = DBHandler(ctx.obj["uri"])
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
        click.echo("Flow created")


@db.command("admin-create", help="Create user in admin panel")
@click.option("--username", help="username admin")
@click.option("--password", help="password admin")
@click.pass_context
def admin_create_user(ctx: click.Context,
                      username: str,
                      password: str):
    """
    Create Admin user to management server with admin panel.

    Args:
        ctx(click.Context): click call context
        username(str): name of admin user
        password(str): password of admin user
    """

    db = DBHandler(ctx.obj["uri"])

    generator = lib.Hash(password,
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
        click.echo(f"Admin created\nusername: "
                   f"{username}\npassword: {password}")


@client.command("send",
                    help="send message to server used API method name.",
                    context_settings=dict(ignore_unknown_options=True,
                                          allow_extra_args=True))
@click.option("-t",
              type=click.Choice(("register_user",
                                 "get_update",
                                 "send_message",
                                 "all_messages",
                                 "add_flow",
                                 "all_flow",
                                 "user_info",
                                 "authentication",
                                 "delete_user",
                                 "delete_message",
                                 "edited_message",
                                 "ping_pong",
                                 "errors")),
              help="MTP protocol API method name, default send_message.",
              default="send_message")
@click.option("-a",
              "--address",
              default="ws://127.0.0.1:8080/ws",
              help="server address and port, default ws://127.0.0.1:8080/ws")
@click.pass_context
@click_async
async def send(ctx: click.Context,
               t: str,
               address: str) -> None:
    """
    Connect and send message protocol method.

    Args:
        ctx: additional arguments in the form of --key=value, the following
             pairs are supported - --uuid=, --auth_id=, --username=,
             --password=
        t: type of message protocol
        address: server address
    """

    try:
        kwargs = dict([item.strip('--').split('=') for item in ctx.args])
    except ValueError:
        click.echo(f"Incorrect key sent={ctx.args}, you must pass --key=value")
        return
    else:
        jsonapi = BaseVersion(version="1.0")
        message = Request(type=t,
                          jsonapi=jsonapi)
        message.parse_file(Path(Path(__file__).parent,
                                "tests",
                                "fixtures",
                                "".join((t, ".json"))))
        message.data = DataRequest()
        message.data.user = []
        message.data.user.append(BaseUser())
        message.data.user[0].uuid = kwargs.setdefault("uuid", "66666")
        message.data.user[0].auth_id = kwargs.setdefault("auth_id", "auth_id")
        message.data.user[0].username = kwargs.setdefault("username", "User")
        message.data.user[0].password = kwargs.setdefault("password", "1234")
        await connect_ws_and_send(message, address)


if __name__ == "__main__":
    cli()
