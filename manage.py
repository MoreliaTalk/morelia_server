import asyncio
import json
import os
import pathlib
import traceback
from ast import literal_eval
from collections import namedtuple
from functools import wraps
from time import process_time, time
from uuid import uuid4

import click
import uvicorn
import websockets.client as websockets
import pathlib

from config import DATABASE, SUPERUSER
from mod import lib
from mod.db import dbhandler
from mod.db.dbhandler import DatabaseWriteError, DatabaseReadError, DatabaseAccessError
from mod.protocol.mtp import api as mtp_api
from mod.protocol.mtp.api import Request


def click_async(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.group()
def cli():
    pass


@cli.group("db", help="manage database")
def db_cli():
    pass


@cli.group("testclient", help="mini-client for server")
@click.option("-a", "--address", default="ws://localhost:8080/ws")
@click.option("--uuid")
@click.option("--auth_id")
@click.pass_context
def client_cli(ctx: click.Context, address: str, uuid: str, auth_id: str):
    ctx.ensure_object(dict)
    ctx.obj["uuid"] = uuid
    ctx.obj["auth_id"] = auth_id
    ctx.obj["address"] = address


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
    uvicorn.run(
        "server:app",
        host=host,
        port=port,
        http="h11",
        ws="websockets",
        log_level=log_level,
        use_colors=use_colors,
        debug=True,
        reload=reload
    )


@db_cli.command("create", help="Create all table with all data")
def db_create():
    start_time = process_time()
    db = dbhandler.DBHandler(uri=DATABASE.get('uri'))
    db.create_table()
    click.echo(f'Table is created at: '
               f'{process_time() - start_time} sec.')


@db_cli.command("delete", help="Delete all table with all data")
def db_delete():
    start_time = process_time()
    db = dbhandler.DBHandler(uri=DATABASE.get('uri'))
    db.delete_table()
    click.echo(f'Table is deleted at: '
               f'{process_time() - start_time} sec.')


@db_cli.command("superuser-create", help="Create superuser in database")
def create_superuser():
    db = dbhandler.DBHandler(uri=DATABASE.get('uri'))
    user_uuid = str(123456789)
    hash_password = SUPERUSER.get('hash_password')
    try:
        db.add_user(uuid=user_uuid,
                    login="login",
                    password="password",
                    hash_password=hash_password,
                    username="superuser",
                    salt=b"salt",
                    key=b"key")
        click.echo("Superuser created")
    except DatabaseWriteError as error:
        click.echo(f'Failed to create a user. Error text: {error}')


@db_cli.command("flow-create", help="Create flow type group in database")
def create_flow():
    db = dbhandler.DBHandler(uri=DATABASE.get('uri'))
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
def admin_create_user(username, password):
    db = dbhandler.DBHandler(uri=DATABASE.get('uri'))

    generator = lib.Hash(password,
                         str(uuid4().hex),
                         key=b"key",
                         salt=b"salt")
    db.add_admin(username=username,
                 hash_password=generator.password_hash())
    click.echo(f"Admin created\nusername: {username}\npassword: {password}")


async def connect_ws_and_send(message, address: str):
    async with websockets.connect(address) as ws:
        await ws.send(message.json())
        response = await ws.recv()
        click.echo(response)


@client_cli.command("register_user", help="send method 'register_user' to server")
@click.option("--login", default="user")
@click.option("--password", default="password")
@click.pass_context
@click_async
async def register_user(ctx, login, password):
    message: Request = mtp_api.Request(type="register_user", jsonapi={"version": "1.0"})
    message.data = mtp_api.DataRequest()
    message.data.user = []
    message.data.user.append(mtp_api.UserRequest())
    message.data.user[0].login = login
    message.data.user[0].password = password

    await connect_ws_and_send(message, ctx.obj["address"])




"""@client_cli.command("send_message", help="send method 'send_message' to server")
@click.pass_context
@click_async
async def send_message(ctx):
    message: Request = mtp_api.Request.parse_file(pathlib.Path(__file__).parent /
                                                  "tests" /
                                                  "fixtures" /
                                                  "send_message.json")

    message.data.user[0].uuid = ctx.obj["uuid"]
    message.data.user[0].auth_id = ctx.obj["auth_id"]
    print(message)

    await connect_ws_and_send(message, ctx.obj["address"])
"""

if __name__ == "__main__":
    cli()
