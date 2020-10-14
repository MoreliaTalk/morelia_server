import sys
import time
import click
import inspect

import sqlobject as orm

from mod import config
from mod import models

# Connect to database
connection = orm.connectionForURI(config.LOCAL_SQLITE)
orm.sqlhub.processConnection = connection

# looking for all Classes listed in the models.py file.
classes = [cls_name for cls_name, cls_obj
           in inspect.getmembers(sys.modules['mod.models'])
           if inspect.isclass(cls_obj)]


@click.command()
@click.option('--table', default='create', help='Create or delete all table \
    whit all data. The operation, by default, creates all tables')
def main(table):
    if table == "create":
        start_time = time.process_time()
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        return print(f"Table is createt at: {time.process_time() - start_time} sec.")
    if table == "superuser":
        models.User(uuid=123456,
                    login="login",
                    password="password",
                    hashPassword="8b915f2f0b0d0ccf27854dd708524d0b5a91bdcd3775c6d3335f63d015a43ce1",
                    username="superuser",
                    salt=b"salt",
                    key=b"key")
        return print("Create user")
    elif table == "delete":
        start_time = time.process_time()
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True, dropJoinTables=True, cascade=True)
        return print(f"Table is deleted at: {time.process_time() - start_time} sec.")
    else:
        return print("ERROR. Function \'--table\' did not work")


if __name__ == "__main__":
    main()
