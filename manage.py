import rich
import typer
import uvicorn

from mod.config.handler import read_config
from mod.db.dbhandler import DBHandler, DatabaseReadError, DatabaseAccessError, DatabaseWriteError

cli = typer.Typer(help="CLI for management MoreliaServer",
                  no_args_is_help=True)

config_option = read_config()


@cli.command()
def create_tables(uri: str = config_option.database.url):
    database = DBHandler(uri)
    try:
        database.create_table()
    except (DatabaseReadError,
            DatabaseAccessError,
            DatabaseWriteError) as err:
        rich.print(f"The database is unavailable, table not created. {err}")
    else:
        rich.print("Tables in db is created.")


@cli.command()
def devserver(host: str = typer.Option("127.0.0.1",
                                       help="Host for running server"),
              port: int = typer.Option(8080,
                                       help="Port for running server"),
              off_uvicorn_logger: bool = typer.Option(True,
                                                      "--off-uvicorn-logger",
                                                      help="Disabled uvicorn logging")):
    if off_uvicorn_logger:
        log_level = "critical"
    else:
        log_level = "debug"

    uvicorn.run("server:app",
                host=host,
                port=port,
                log_level=log_level,
                debug=True,
                reload=True)


if __name__ == "__main__":
    cli()
