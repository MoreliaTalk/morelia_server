import sys
import time
import inspect
from uuid import uuid4

import sqlobject as orm
import click

from mod import config
from mod import models


@click.command()
@click.option("--db",
              type=click.Choice(["create", "delete"]),
              help='Create or delete all table '
              'with all data. Оperation, '
              'by default, creates all tables')
@click.option('--table',
              type=click.Choice(["superuser", "flow"]),
              help='Creating records in the database.'
              'You can create a superuser or flow type "group".')
def main(db, table):
    # Connect to database
    connection = orm.connectionForURI(config.LOCAL_SQLITE)
    orm.sqlhub.processConnection = connection

    # looking for all Classes listed in models.py
    classes = [cls_name for cls_name, cls_obj
               in inspect.getmembers(sys.modules['mod.models'])
               if inspect.isclass(cls_obj)]

    if db == "create":
        start_time = time.process_time()
        for item in classes:
            # Create tables in database for each class
            # that is located in models module
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        click.echo(f'Table is createt at: '
                   f'{time.process_time() - start_time} sec.')
    elif db == "delete":
        start_time = time.process_time()
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True, dropJoinTables=True, cascade=True)
        click.echo(f'Table is deleted at: '
                   f'{time.process_time() - start_time} sec.')
    elif table == "superuser":
        hash_password = "8b915f2f0b0d0ccf27854dd708524d0b5a91bdcd3775c6d3335f63d015a43ce1"
        try:
            models.UserConfig(uuid=str(123456789),
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
        user_uuid = str(123456789)
        hash_password = "8b915f2f0b0d0ccf27854dd708524d0b5a91bdcd3775c6d3335f63d015a43ce1"
        try:
            new_user = models.UserConfig(uuid=user_uuid,
                                         login="login",
                                         password="password",
                                         hashPassword=hash_password,
                                         username="superuser",
                                         salt=b"salt",
                                         key=b"key")
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
    else:
        click.echo("ERRROOOOR")


if __name__ == "__main__":
    main()
