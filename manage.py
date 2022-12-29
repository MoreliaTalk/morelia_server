from enum import Enum
import rich
import typer
import uvicorn

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
              use_colors: bool = typer.Option(True, help="Enable using colors in terminal")):
    uvicorn.run("server:app",
                host=host,
                port=port,
                http="h11",
                ws="websockets",
                use_colors=use_colors,
                debug=True,
                reload=True)


if __name__ == "__main__":
    cli()
