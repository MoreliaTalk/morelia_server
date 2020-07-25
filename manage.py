import sys
import time
import click
import inspect

import sqlobject as orm

from mod import config
from mod import models


connection = orm.connectionForURI(config.LOCAL_SQLITE)
orm.sqlhub.processConnection = connection


classes = [cls_name for cls_name, cls_obj in inspect.getmembers(sys.modules['mod.models']) if inspect.isclass(cls_obj)]


@click.command()
@click.option('--table', default='create', help='Create or delete all table \
    whit all data. The operation, by default, creates all tables')
def main(table):
    if table == "create":
        start_time = time.process_time()
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        print(f"Table is createt at: {time.process_time() - start_time} sec.")
        return
    elif table == "delete":
        start_time = time.process_time()
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True, dropJoinTables=True, cascade=True)
        print(f"Table is deleted at: {time.process_time() - start_time} sec.")
        return
    else:
        return print("ERROR. Function \'--table\' did not work")


if __name__ == "__main__":
    main()
