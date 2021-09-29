# Morelia Server - messenger server for Morelia Network #

Language [EN](./README_ENG.md), [RU](./README.md)

## There are two brunches in repository ##

[master](https://github.com/MoreliaTalk/morelia_server/tree/master) - stable branch.

[develop](https://github.com/MoreliaTalk/morelia_server/tree/develop) - branch to add new functionality.

## Development applies ##

* [Python 3.9](https://www.python.org/) - programming language

* [FastAPI](https://fastapi.tiangolo.com) - basic framework

* [SQLObject](http://sqlobject.org) - ORM for working with the database

* [Pydantic](https://pydantic-docs.helpmanual.io) - data validation

* [Starlette](https://www.starlette.io) - lightweight ASGI framework

* [websockets](https://pypi.org/project/websockets/) - Python implementation of Websockets protocol (RFC 6455 & 7692)

## Repository description ##

* /mod
  * api.py - module is responsible for description of API, as well as validation of data.
  * error.py - module is responsible for storing error codes.
  * controller.py - module is responsible for implementing methods described in [Morelia Protocol](https://github.com/MoreliaTalk/morelia_protocol/blob/master/README.md).
  * lib.py - module is responsible for hashing password, comparing password with its hash sum, and creating a hash for auth_id.
  * models.py - module is responsible for describing database tables to work through ORM.
  * logging.py - logging configuration module.
* /templates - templates for displaying server statistics in browser.
  * base.html - base template with basic elements of menu, it is implemented in every working template.
  * index.html - working homepage template.
  * status.thml - working page template with status of server.
* server.py - basic server code.
* manage.py - migration manager for database (creating and deleting database tables).
* /tests
  * fixtures/
    * api.json - json-file with pre-prepared data, to conduct tests.
  * test_api.py - validation tests.
  * test_controller.py - tests to check class that is responsible for processing protocol methods.
  * test_lib.py - hash function tests.
* debug_server.py - A wrapper for server.py to debug through a utility `pdb`.
* example_config.ini - file containing the example server settings, just rename it to `config.ini` before starting the server.
* client.py - mini client to check the server operation.

## Installing ##

Install [Python](https://www.python.org/downloads/) version 3.8 or higher.

Download and install latest version [git](https://git-scm.com/downloads).

If you need a GUI, install [GitHub Desktop](https://desktop.github.com/).

Set up Git or GitHub Desktop by entering your `username` and `email` from an account created on [github](https://www.github.com).

## Fork repository Morelia Server ##

If you are not on the GitHub project team, you must first fork the Morelia Server repository to yourself by going to [link](https://github.com/MoreliaTalk/morelia_server/fork).

## Cloning a repository to a local computer ##

Clone repository to your local computer using command line and `git`

```cmd
git clone https://github.com/{username}/morelia_server.git
cd morelia_server
```

Switching to `develop` branch

```cmd
git checkout develop
```

Synchronizing your fork with original repository `upstream` Morelia Server

```cmd
git remote add upstream https://github.com/MoreliaTalk/morelia_server.git
```

Check if repository `upstream` appeared in the list of deleted repositories

```cmd
git remote -v
> origin    https://github.com/{username}/morelia_server.git (fetch)
> origin    https://github.com/{username}/morelia_server.git (push)
> upstream  https://github.com/MoreliaTalk/morelia_server.git (fetch)
> upstream  https://github.com/MoreliaTalk/morelia_server.git (push)
```

If using `GitHub`, select `Clone repository...` from `File` menu and follow instructions

## Configuring the Pipenv Virtual Environment ##

To work with the project it is necessary to install the libraries that it uses and configure the so-called `virtual environment` or `virtualenv`, for this purpose the utility [Pipenv](https://github.com/pypa/pipenv)

If pipenv is not installed, run

```cmd
python -m pip install pipenv
```

Create a virtual environment in project directory

```cmd
pipenv shell
```

Install all required libraries from Pipfile

```cmd
pipenv install --ignore-pipfile
```

## Before starting the server - use the configuration manager ##

Before you start the server you need to make some settings (create a database, tables and add the first user - administrator)

Create a database with empty tables:

```cmd
pipenv run python ./manage.py --db create
```

If you want to delete all tables in the created database (WARNING only tables are deleted, the database is not deleted):

```cmd
pipenv run python ./manage.py --db delete
```

Add the administrator in the created database:

```cmd
pipenv run python ./manage.py --table superuser
```

Additionally, you can create a `flow` with the group type:

```cmd
pipenv run python ./manage.py --table flow
```

Information about all the features of the configuration manager:

```cmd
pipenv run python ./manage.py --help
```

## Server startup ##

To start server, use command:

```cmd
uvicorn server:app --host 0.0.0.0 --port 8000 --reload --use-colors --http h11 --ws websockets
```

Additional parameters that can be sent to server:

`--log-level <str>` - Set the log level. Options: 'critical', 'error', 'warning', 'info', 'debug', 'trace'. Default: 'info'.

`--use-colors / --no-use-colors` - Enable / disable colorized formatting of the log records, in case this is not set it will be auto-detected. This option is ignored if the `--log-config` CLI option is used.

`--loop <str>` - Set the event loop implementation. The uvloop implementation provides greater performance, but is not compatible with Windows or PyPy. Options: 'auto', 'asyncio', 'uvloop'. Default: 'auto'.

`--http <str>` - Set the HTTP protocol implementation. The httptools implementation provides greater performance, but it not compatible with PyPy, and requires compilation on Windows. Options: 'auto', 'h11', 'httptools'. Default: 'auto'.

`--ws <str>` - Set the WebSockets protocol implementation. Either of the websockets and wsproto packages are supported. Use 'none' to deny all websocket requests. Options: 'auto', 'none', 'websockets', 'wsproto'. Default: 'auto'.

`--lifespan <str>` - Set the Lifespan protocol implementation. Options: 'auto', 'on', 'off'. Default: 'auto'.

`--interface` - Select ASGI3, ASGI2, or WSGI as the application interface. Note that WSGI mode always disables WebSocket support, as it is not supported by the WSGI interface. Options: 'auto', 'asgi3', 'asgi2', 'wsgi'. Default: 'auto'.

`--limit-concurrency <int>` - Maximum number of concurrent connections or tasks to allow, before issuing HTTP 503 responses. Useful for ensuring known memory usage patterns even under over-resourced loads.

`--limit-max-requests <int>` - Maximum number of requests to service before terminating the process. Useful when running together with a process manager, for preventing memory leaks from impacting long-running processes.

`--backlog <int>` - Maximum number of connections to hold in backlog. Relevant for heavy incoming traffic. Default: 2048

`--ssl-keyfile <path>` - SSL key file

`--ssl-certfile <path>` - SSL certificate file

`--ssl-version <int>` - SSL version to use (see stdlib ssl module's)

`--ssl-cert-reqs <int>` - Whether client certificate is required (see stdlib ssl module's)

`--ssl-ca-certs <str>` - CA certificates file

`--ssl-ciphers <str>` - Ciphers to use (see stdlib ssl module's)

`--timeout-keep-alive <int>` - Close Keep-Alive connections if no new data is received within this timeout. Default: 5.

## Running the server in DEBUG mode ##

To easily start the server in debug mode, all you need to do is run `debug_server.py`:

```cmd
pipenv run python ./debug_server.py
```

## Checking server availability with the built-in client ##

To test the server, run the mini client `client.py` in the console:

```cmd
pipenv run python -i ./client.py
```

After launching, the client will send an authorization message (AUTH) to the server, the server's response will be displayed in the console, after which `python` will go into interactive line mode `>>>`, so that it is possible to perform additional checks.

In the interactive console, there will be one function available to send `end_message` which takes two arguments `message` message and `uri` server address. In the argument `message` you need to pass an object with type "dict" or "str", you can use ready-made examples of queries: AUTH, GET_UPDATE, ADD_FLOW, ALL_FLOW. In the argument you must pass an object with type "str", you can use ready examples of server address: LOCALHOST.

```py
>>> send_message(GET_UPDATE, LOCALHOST)
```

If no arguments are passed to the function, the default is to send an AUTH message to LOCALHOST.

## Creating a pool-request to make changes to development branch Morelia Server ##

Getting latest changes from development branch Morelia Server

```cmd
git pull upstream develop
```

Sending changes to development branch of your fork

```cmd
git push
```

To create a pull-request, you need to go to [GitHub](https://www.github.com), select your fork and click on `New pull request` in right-hand menu, then select branch from which you want to push changes to Morelia Server development branch and click `Create pull request`.

## Code style requirements ##

Before starting work, it is recommended that you read [PEP 8 - Python Code Writing Guide](https://pythonworld.ru/osnovy/pep-8-rukovodstvo-po-napisaniyu-koda-na-python.html). Be sure to use a linter (flake8, pylint or similar).

## Logging ##

Library is used [loguru](https://github.com/Delgan/loguru)

Logging levels you can use in your code:

```py
Level name | Logger method

DEBUG      | logger.debug()
INFO       | logger.info()
SUCCESS    | logger.success()
WARNING    | logger.warning()
ERROR      | logger.error()
           | logger.exception()
CRITICAL   | logger.critical()
```

## Writing and running tests ##

Built-in Unittest module is used to write tests.

To run tests, run (replace asterisk with test name)

```cmd
pipenv run python -v ./tests/test_*.py
```

## Running the debugger ##

To run debugger in a working server environment, through console

```cmd
python -m pdb ./debug_server.py
```

To get help in debug mode

```cmd
(pdb) help
```

## Contacts ##

[Telegram](https://t.me/joinchat/LImHShzAmIWvpMxDTr5Vxw) - a group where pressing issues are discussed.

[Slack](www.moreliatalk.slack.com) - an alternative way of discussing the project.

## License ##

Copyright (c) 2020 - present [NekrodNIK](https://github.com/NekrodNIK), [Stepan Skriabin](https://github.com/stepanskryabin), [rus-ai](https://github.com/rus-ai) and other. Look at the file AUTHORS.md for a complete list.

Morelia Server is licensed under the GNU Lesser General Public License version 3 or later (LGPL-3.0-or-later). See the COPYING.LESSER file for details.

