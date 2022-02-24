import asyncio
import pathlib
from functools import wraps
from time import process_time, time
from uuid import uuid4

import click
import uvicorn
import websockets

from mod import lib
from mod.db import dbhandler
from mod.db.dbhandler import DatabaseWriteError
from mod.db.dbhandler import DatabaseReadError
from mod.db.dbhandler import DatabaseAccessError
from mod.config.config import ConfigHandler
from mod.protocol.mtp import api as mtp_api
from mod.protocol.mtp.api import Request

config = ConfigHandler()
config_option = config.read()


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
def client_cli():
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
    db = dbhandler.DBHandler(uri=config_option.uri)
    db.create_table()
    click.echo(f'Table is created at: '
               f'{process_time() - start_time} sec.')


@db_cli.command("delete", help="Delete all table with all data")
def db_delete():
    start_time = process_time()
    db = dbhandler.DBHandler(uri=config_option.uri)
    db.delete_table()
    click.echo(f'Table is deleted at: '
               f'{process_time() - start_time} sec.')


@db_cli.command("superuser-create", help="Create superuser in database")
def create_superuser():
    db = dbhandler.DBHandler(uri=config_option.uri)
    user_uuid = str(123456789)
    hash_password = config.SUPERUSER.get('hash_password')
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
    db = dbhandler.DBHandler(uri=config_option.uri)
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
    db = dbhandler.DBHandler(uri=config_option.uri)

    generator = lib.Hash(password,
                         str(uuid4().hex),
                         key=b"key",
                         salt=b"salt")
    db.add_admin(username=username,
                 hash_password=generator.password_hash())
    click.echo(f"Admin created\nusername: {username}\npassword: {password}")


async def connect_ws_and_send(message, address: str):
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
            await ws.close()


@client_cli.command("send", help="send message to server",
                    context_settings=dict(
                        ignore_unknown_options=True,
                        allow_extra_args=True,
                    ))
@click.option("-t", default="send_message")
@click.option("-a", "--address", default="ws://127.0.0.1:8080/ws")
@click.pass_context
@click_async
async def all_messages(ctx, t, address):
    kwargs = dict([item.strip('--').split('=') for item in ctx.args])
    message: Request = mtp_api.Request.parse_file(pathlib.Path(__file__).parent /
                                                  "tests" /
                                                  "fixtures" /
                                                  (t + ".json"))
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

        data = exec(kw_request + f" = '{kwargs[kw]}'", {
            "__builtins__": {},
            "mes_dict": mes_dict
        })

    await connect_ws_and_send(message, address)


if __name__ == "__main__":
    cli()
