from enum import Enum
import rich
import typer
import uvicorn
import logging as standard_logging

cli = typer.Typer(help="CLI for management MoreliaServer",
                  no_args_is_help=True)


@cli.command()
def production_server():
    rich.print("Welcome to cli")


@cli.command("devserver")
def devserver(host: str = typer.Option("127.0.0.1",
                                       help="Host for running server"),
              port: int = typer.Option(8080,
                                       help="Port for running server"),
              on_uvicorn_logger: bool = typer.Option(False, help="Activate uvicorn logging")):
    if on_uvicorn_logger:
        uvicorn_logger = standard_logging.getLogger("uvicorn")
        uvicorn_logger.handlers.clear()

    uvicorn.run("server:app",
                host=host,
                port=port,
                debug=True,
                reload=True)


if __name__ == "__main__":
    cli()
