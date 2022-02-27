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
from os.path import join
from pathlib import Path
import random
from time import process_time
from time import time
from uuid import uuid4

import click
import uvicorn
import websockets

from mod import lib
from mod.config.config import ConfigHandler
from mod.db.dbhandler import DatabaseAccessError
from mod.db.dbhandler import DatabaseReadError
from mod.db.dbhandler import DatabaseWriteError
from mod.db.dbhandler import DBHandler
from mod.protocol.mtp import api as mtp_api
from mod.protocol.mtp.api import Request

config = ConfigHandler()
config_option = config.read()

SYMBOLS_FOR_RANDOM = "abcdefghijklmnopqrstuvwxyz \
                      ABCDEFGHIJKLMNOPQRSTUVWXYZ \
                      1234567890"


async def connect_ws_and_send(message, address: str):
    """
    Connect and send message to address.

    Args:
        message: message for send
        address(str): server address
    """
    try:
        ws = await websockets.connect(address)
    except ConnectionRefusedError:
        click.echo("Unable to connect to the server, please check the server")
    else:
        await ws.send(message.json())
        try:
            response = await ws.recv()
        except websockets.ConnectionClosedError as error:
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


@click.group()
def cli():
    """
    Group for all command.
    """
    pass


@cli.group("db", help="manage database")
def db_cli():
    """
    Group for db manipulation command.
    """
    pass


@cli.group("testclient", help="mini-client for server")
def client_cli():
    """
    Group for client command.
    """
    pass


@cli.command("runserver", help="run app using the dev server")
@click.option("-h", "--host", default="localhost")
@click.option("-p", "--port", default=8080)
@click.option("--log-level", default="debug")
@click.option("--use-colors", default=True)
@click.option("-r", "--reload", default=True)
def run(host: str,
        port: int,
        log_level: str,
        use_colors: bool,
        reload: bool):
    """
    Run server.

    Args:
        host(str): host for run
        port(str):port for run
        log_level(str): level logs
        use_colors(bool): enable use colors in terminal
        reload(bool): enable hot reload
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


@db_cli.command("create", help="Create all table with all data")
def db_create():
    """
    Create database, and create all table which contain in models.
    """

    start_time = process_time()
    db = DBHandler(uri=config_option.uri)
    db.create_table()
    click.echo(f'Table is created at: '
               f'{process_time() - start_time} sec.')


@db_cli.command("delete", help="Delete all table with all data")
def db_delete():
    """
    Delete all tables which contains data.
    This function not delete database file.
    """

    start_time = process_time()
    db = DBHandler(uri=config_option.uri)
    db.delete_table()
    click.echo(f'Table is deleted at: '
               f'{process_time() - start_time} sec.')


@db_cli.command("user-create", help="Creates a user in the database, \
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
def create_user(login: str, username: str, password: str):
    """
    Create user in database.

    Args:
        login(str): user login
        username(str): username
        password(str): user password
    """

    db = DBHandler(uri=config_option.uri)
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


@db_cli.command("flow-create", help="Create flow type group in database")
def create_flow():
    """
    Creating and adding test flow (group) in database.
    """

    db = DBHandler(uri=config_option.uri)
    user_uuid = str(123456789)
    try:
        new_user = db.get_user_by_uuid(uuid=user_uuid)
        new_flow = db.add_flow(uuid=str(uuid4().hex),
                               users=[user_uuid],
                               time_created=int(time()),
                               flow_type="group",
                               title="Test",
                               info="Test flow",
                               owner=user_uuid)
        new_flow.addUserConfig(new_user)
        click.echo("Flow created")
    except (DatabaseReadError,
            DatabaseAccessError,
            DatabaseWriteError) as error:
        click.echo(f'Failed to create a flow. Error text: {error}')


@db_cli.command("admin-create", help="Create user in admin panel")
@click.option("--username", help="username admin")
@click.option("--password", help="password admin")
def admin_create_user(username,
                      password):
    """
    Create Admin user to management server with admin panel.

    Args:
        username: name of admin user
        password: password of admin user
    """

    db = DBHandler(uri=config_option.uri)

    generator = lib.Hash(password,
                         str(uuid4().hex),
                         key=b"key",
                         salt=b"salt")
    db.add_admin(username=username,
                 hash_password=generator.password_hash())
    click.echo(f"Admin created\nusername: {username}\npassword: {password}")


@client_cli.command("send",
                    help="send message to server",
                    context_settings=dict(ignore_unknown_options=True,
                                          allow_extra_args=True))
@click.option("-t", help="type message mtp protocol", default="send_message")
@click.option("-a", "--address", default="ws://127.0.0.1:8080/ws")
@click.pass_context
@click_async
async def send(ctx, t, address):
    """
    Connect and send message protocol method.

    Args:
        ctx(click.context): click run context
        t(str): type message protocol
        address(str): server address
    """

    kwargs = dict([item.strip('--').split('=') for item in ctx.args])
    message = mtp_api.Request.parse_file(
        Path(Path(__file__).parent, "tests", "fixtures", join(t, ".json"))
    )

    message.data.user.append(mtp_api.BaseUser())

    mes_dict = message.dict()
    for kw in kwargs:
        kw_request = "mes_dict"
        for kw_sub in kw.split("."):
            try:
                kw_sub = int(kw_sub)
            except ValueError:
                kw_request += f'["{kw_sub}"]'
            else:
                kw_request += f'[{kw_sub}]'

        exec(kw_request + f" = '{kwargs[kw]}'", {
            "__builtins__": {},
            "mes_dict": mes_dict
        })

    await connect_ws_and_send(message, address)


if __name__ == "__main__":
    cli()
