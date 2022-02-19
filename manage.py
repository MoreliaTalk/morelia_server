import click
import uvicorn


@click.group()
def cli():
    pass


@cli.command("run", help="run app using the dev server")
@click.option("-h", "--host", default="localhost")
@click.option("-p", "--port", default=8080)
@click.option("--log-level", default="debug")
@click.option("--use-colors", default=True)
@click.option("-r", "--reload", default=True)
def run(host: str,
        port: int,
        log_level: str,
        use_colors: bool,
        reload: bool):
    uvicorn.run(
        "server:app",
        host=host,
        port=port,
        http="h11",
        ws="websockets",
        log_level=log_level,
        use_colors=use_colors,
        debug=True,
        reload=reload
    )


if __name__ == "__main__":
    cli()
