import sqlobject as orm
import time
import click

from mod import config
from mod import models


connection = orm.connectionForURI(config.LOCAL_SQLITE)
orm.sqlhub.processConnection = connection


@click.command()
@click.option('--table', default='create', help='Create or delete all table \
    whit all data. The operation, by default, creates all tables')
def main(table):
    if table == "create":
        start_time = time.process_time()
        models.User.createTable(ifNotExists=True)
        models.Flow.createTable(ifNotExists=True)
        models.Message.createTable(ifNotExists=True)
        models.Errors.createTable(ifNotExists=True)
        print(f"Table is createt at: {time.process_time() - start_time} sec.")
        return
    elif table == "delete":
        start_time = time.process_time()
        models.User.dropTable(
            ifExists=True, dropJoinTables=True, cascade=True)
        models.Flow.dropTable(
            ifExists=True, dropJoinTables=True, cascade=True)
        models.Message.dropTable(
            ifExists=True, dropJoinTables=True, cascade=True)
        models.Errors.dropTable(
            ifExists=True, dropJoinTables=True, cascade=True)
        print(f"Table is deleted at: {time.process_time() - start_time} sec.")
        return
    else:
        return print("ERROR. Function \'--table\' did not work")


if __name__ == "__main__":
    main()
