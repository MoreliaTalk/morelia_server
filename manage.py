from pathlib import Path
from time import time
from typing import Optional
from uuid import uuid4

import tomli_w
import typer
import uvicorn
from faker import Faker
from loguru import logger
from rich.console import Console
from rich import box
from rich.table import Table

from mod.config.handler import read_config
from mod.config.models import ConfigModel
from mod.db.dbhandler import DBHandler, DatabaseReadError, DatabaseAccessError, DatabaseWriteError
from mod.lib import Hash

cli = typer.Typer(help="CLI for management MoreliaServer",
                  no_args_is_help=True)

rich_output = Console()
fake_data_generator = Faker()

logger.disable("mod.config.handler")
config_option = read_config()


@cli.command()
def devserver(host: str = typer.Option("127.0.0.1",
                                       help="Host for running server"),
              port: int = typer.Option(8080,
                                       help="Port for running server"),
              on_uvicorn_logger: bool = typer.Option(False,
                                                     "--on-uvicorn-logger",
                                                     help="Disabled uvicorn logging")):
    if on_uvicorn_logger:
        log_level = "debug"
    else:
        log_level = "critical"

    uvicorn.run(app="server:app",
                host=host,
                port=port,
                log_level=log_level,
                debug=True,
                reload=True)


@cli.command()
def restore_config():
    is_confirm = typer.confirm("This action is not reversible. "
                               "The config will be overwritten "
                               "with default data. Continue?")

    if is_confirm:
        default_dict = ConfigModel().dict()
        default_toml = tomli_w.dumps(default_dict)

        with Path("config.toml").open("w") as config_file:
            config_file.write(default_toml)

        rich_output.print("Successful restore config")
    else:
        rich_output.print("Canceled!")


@cli.command()
def create_tables():
    database = DBHandler(config_option.database.url)
    try:
        database.create_table()
    except (DatabaseReadError,
            DatabaseAccessError,
            DatabaseWriteError) as err:
        rich_output.print(f"[red]The database is unavailable, "
                          f"table not created. {err}")
    else:
        rich_output.print("[green]Tables in db successful created.")


@cli.command()
def delete_tables():
    database = DBHandler(config_option.database.url)
    try:
        database.delete_table()
    except (DatabaseReadError,
            DatabaseAccessError,
            DatabaseWriteError) as err:
        rich_output.print(f"[red]The database is unavailable, "
                          f"table not deleted. {err}")
    else:
        rich_output.print("[green]Tables in db successful deleted.")


@cli.command()
def create_user(login: str = typer.Argument(..., help="Login"),
                username: Optional[str] = typer.Option(None, help="Username. If value is set to None, "
                                                                  "generated random username is used."),
                password: Optional[str] = typer.Option(None, help="Password. If value is set to None, "
                                                                  "generated random password is used.")):
    if username is None:
        username = fake_data_generator.profile()["username"]

    if password is None:
        password = fake_data_generator.password()

    db = DBHandler(config_option.database.url)

    uuid = str(uuid4().int)

    try:
        db.add_user(uuid=uuid,
                    login=login,
                    password=password,
                    hash_password=Hash(password, uuid).password_hash(),
                    username=username,
                    salt=b"salt",
                    key=b"key")
    except DatabaseWriteError:
        rich_output.print("[red]Database write error, user not created. Check that tables is exist.")
    else:
        output_table = Table(box=box.SQUARE,
                             header_style="bold green")

        output_table.add_column("UUID", justify="center")
        output_table.add_column("Login", justify="center")
        output_table.add_column("Username", justify="center")
        output_table.add_column("Password", justify="center")

        output_table.add_row(f"{uuid}",
                             f"{login}",
                             f"{username}",
                             f"{password}",
                             style="bold bright_yellow")

        rich_output.print("User successful created:", style="bold green")
        rich_output.print(output_table)


@cli.command()
def create_group(owner_login: str) -> None:
    db = DBHandler(config_option.database.url)

    try:
        user = db.get_user_by_login(login=owner_login)
    except DatabaseWriteError:
        rich_output.print("[red]Database write error, user not created. Check that tables is exist")
    else:
        new_flow = db.add_flow(uuid=str(uuid4().int),
                               users=[user.uuid],
                               time_created=int(time()),
                               flow_type="group",
                               title="Test",
                               info="Test flow",
                               owner=user.uuid)
        new_flow.addUserConfig(user)
        rich_output.print("Flow created")


if __name__ == "__main__":
    cli()
