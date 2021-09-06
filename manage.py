"""
    Copyright (c) 2020 - present NekrodNIK, Stepan Scryabin, rus-ai and other.
    Look at the file AUTHORS.md(located at the root of the project) to get the full list.

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

import sys
from time import time, process_time
import inspect
from uuid import uuid4
import configparser

import sqlobject as orm
import click

from mod import models

# ************** Read "config.ini" ********************
config = configparser.ConfigParser()
config.read('config.ini')
logging = config['LOGGING']
database = config["DATABASE"]
superuser = config["SUPERUSER"]
# ************** END **********************************


@click.command()
@click.option("--db",
              type=click.Choice(["create", "delete"]),
              help='Create or delete all table '
              'with all data. Оperation, '
              'by default, creates all tables')
@click.option('--table',
              type=click.Choice(["superuser", "flow"]),
              help='Creating records in the database. '
              'You can create a superuser or flow type "group".')
def main(db, table):
    # Connect to database
    connection = orm.connectionForURI(database.get("uri"))
    orm.sqlhub.processConnection = connection

    # looking for all Classes listed in models.py
    classes = [cls_name for cls_name, cls_obj
               in inspect.getmembers(sys.modules['mod.models'])
               if inspect.isclass(cls_obj)]

    if db == "create":
        start_time = process_time()
        for item in classes:
            # Create tables in database for each class
            # that is located in models module
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        click.echo(f'Table is createt at: '
                   f'{process_time() - start_time} sec.')
    elif db == "delete":
        start_time = process_time()
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True, dropJoinTables=True, cascade=True)
        click.echo(f'Table is deleted at: '
                   f'{process_time() - start_time} sec.')

    user_uuid = str(123456789)
    hash_password = superuser.get('hash_password')
    if table == "superuser":
        try:
            models.UserConfig(uuid=user_uuid,
                              login="login",
                              password="password",
                              hashPassword=hash_password,
                              username="superuser",
                              salt=b"salt",
                              key=b"key")
            click.echo("Superuser created")
        except orm.dberrors.OperationalError as error:
            click.echo(f'Failed to create a user. Error text: {error}')
    elif table == "flow":
        try:
            new_user = models.UserConfig.selectBy(uuid=user_uuid).getOne()
            new_flow = models.Flow(uuid=str(uuid4().hex),
                                   timeCreated=int(time()),
                                   flowType="group",
                                   title="Test",
                                   info="Test flow",
                                   owner=user_uuid)
            new_flow.addUserConfig(new_user)
            click.echo("Flow created")
        except orm.dberrors.OperationalError as error:
            click.echo(f'Failed to create a flow. Error text: {error}')


if __name__ == "__main__":
    main()
