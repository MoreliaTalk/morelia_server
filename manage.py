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

from time import time
from time import process_time
from uuid import uuid4

import click

from mod import lib
from mod.db import dbhandler
from mod.db.dbhandler import DatabaseWriteError
from mod.db.dbhandler import DatabaseReadError
from mod.db.dbhandler import DatabaseAccessError
from mod.config import DATABASE
from mod.config import SUPERUSER


@click.group()
def cli():
    pass


@cli.command("db-create", help="Create all table with all data")
def db_create():
    start_time = process_time()
    db = dbhandler.DBHandler(uri=DATABASE.get('uri'))
    db.create_table()
    click.echo(f'Table is created at: '
               f'{process_time() - start_time} sec.')


@cli.command("db-delete", help="Delete all table with all data")
def db_delete():
    start_time = process_time()
    db = dbhandler.DBHandler(uri=DATABASE.get('uri'))
    db.delete_table()
    click.echo(f'Table is deleted at: '
               f'{process_time() - start_time} sec.')


@cli.command("superuser-create", help="Create superuser in database")
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


@cli.command("flow-create", help="Create flow type group in database")
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


@cli.command("admin-create", help="Create user in admin panel")
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


if __name__ == "__main__":
    cli()
