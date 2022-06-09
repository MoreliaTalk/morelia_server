# Morelia Server - server for MoreliaTalk messenger #


![tests](https://github.com/MoreliaTalk/morelia_server/workflows/Test%20and%20Linting/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/MoreliaTalk/morelia_server/badge.svg?branch=master)](https://coveralls.io/github/MoreliaTalk/morelia_server)

Language [EN](./README_ENG.md), [RU](./README.md)

##re are 2 branches in repository ##

[Master](https://github.com/MoreliaTalk/morelia_server/tree/master) - stable branch.

## Applied in development ##

* [Python 3.10](https://www.python.org/) - programming language

* [Starlette](https://www.starlette.io/) - main framework

* [SQLObject](http://sqlobject.org) - ORM for working with database

* [Pydantic](https://pydantic-docs.helpmanual.io) - data validation

* [Starlette](https://www.starlette.io) - lightweight ASGI framework/toolkit

* [websockets](https://pypi.org/project/websockets/) - implementation of Websockets protocol in Python (RFC 6455 & 7692)

## Repository description ##

*/mod
  */config
    * config.py - module is responsible for working with config.ini configuration file
    * validator.py - module for validating configuration file
  */db
    * dbhandler.py - module is designed to execute queries to database
    * models.py - module is responsible for describing database tables for working through ORM.
  * /protocol
    */matrix
      * api.py - module is responsible for description of API, as well as data validation.
      * worker.py - protocol implementation
    * /mtp
      * api.py - module is responsible for description of API, as well as data validation.
      * worker.py - module is responsible for implementing methods described in [Morelia Protocol](https://github.com/MoreliaTalk/morelia_protocol/blob/master/README.md).
    * error.py - module is responsible for checking and generating responses with error codes.
    * controller.py - module processes request according to protocol type
    * lib.py - module is responsible for hashing password, comparing password with its hash sum, creating a hash for auth_id.
    * log_handler.py - logging configuration module.
    * config.py - module reads settings from config.ini
* server.py - main server code
* manage.py - cli tool for working with server (launch, test client, work with database, etc.)
* /tests
  * fixtures/ - json files with pre-prepared data for testing.
  * config.ini - server config for testing
  * test_*.py - tests
* example_config.ini - a file containing an example of server settings, just rename or copy to `config.ini` before starting server.

## Installation ##

Install [Python](https://www.python.org/downloads/) version 3.10 or higher.

Download and install latest version of [git](https://git-scm.com/downloads).

If you need a GUI, install [GitHub Desktop](https://desktop.github.com/).

Set up Git or GitHub Desktop by entering your `username` and `email` from account created on [github](https://www.github.com).

## Fork of Morelia Server repository ##

If you are not included in team on GitHub of project,n you must first fork Morelia Server repository to yourself by following [link] (https://github.com/MoreliaTalk/morelia_server/fork).

## Clone repository on local machine ##

Clone repository to your local computer using command line and `git`

```cmd
git clone https://github.com/{username}/morelia_server.git
cd morelia_server
```

Synchronize your fork with original `upstream` Morelia Server repository

```cmd
git remote add upstream https://github.com/MoreliaTalk/morelia_server.git
```

Checking if `upstream` repository appears in list of remote repositories

```cmd
git remote -v
> origin https://github.com/{username}/morelia_server.git (fetch)
> origin https://github.com/{username}/morelia_server.git (push)
> upstream https://github.com/MoreliaTalk/morelia_server.git (fetch)
> upstream https://github.com/MoreliaTalk/morelia_server.git (push)
```

When using `GitHub`, select `Clone repository...` from `File` menu,n follow instructions

## Set up Pipenv virtual environment ##

To work with project, you need to install libraries that it uses and configure so-called. `virtual desktop` or `virtualenv`, for this use [Pipenv] utility (https://github.com/pypa/pipenv)

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

## Before starting server - use settings manager ##

Before starting server, you need to make some settings (create a database, tables and add first user - administrator)

Open `example_config.ini` file, find URI parameter, replace it with database path, example:
`URI = 'sqlite:db_sqlite.db' `.

Create `config.ini`, database file and create administrator:

```cmd
pipenv run python ./manage.py run init
```

If you need to delete all tables in created database (WARNING, only tables are deleted, database is not deleted):

```cmd
pipenv run python ./manage.py delete db
```

Additionally, you can create a `flow` with a group type:

```cmd
pipenv run python ./manage.py create flow
```

Information about all features of settings manager:

```cmd
pipenv run python ./manage.py --help
```

## Start server in develop mode ##

To start server, use command:

```cmd
pipenv run python ./manage.py run devserver
```

## Starting server in normal mode ##

To start server, use command:

```cmd
pipenv run python ./manage.py run server
```

Options:

`--host <str>` - host address

`--port <int>` - port on which server will be launched

`--log-level <str>` - sets logging level. Options: "critical", "error", "warning", "info", "debug", "trace". Default: "debug".

`--use-colors` - turns color highlighting of logs on and off

`--reload` - activates/deactivates automatic restart of server when its code changes


## Checking health of server using built-in client ##

To check if server is working, run built-in mini-client in `manage.py`:

```cmd
pipenv run python manage.py client send
```

Note: before starting client, you need to start server

## Create a pull request to make changes to Morelia Server master branch ##

Getting latest changes from Morelia Server master branch

```cmd
git pull upstream master
```

Pushing changes to master branch of your fork

```cmd
git push
```

To create a pull request, you need to go to [GitHub](https://www.github.com), select your fork and click on `New pull request` in right menu,n select branch from which changes will be transferred to Morelia Server master branch and click `Create pull request`.

## Code style requirements ##

Before getting started, it is recommended to read [PEP 8 - Python Code Guide](https://pythonworld.ru/osnovy/pep-8-rukovodstvo-po-napisaniyu-koda-na-python.html). Be sure to use a linter (flake8, pylint or similar).

## Logging ##

The [loguru] library is used (https://github.com/Delgan/loguru)

Logging levels that can be used in code:

```
Level name | logger method

DEBUG | logger.debug()
INFO | logger.info()
SUCCESS | logger.success()
WARNING | logger.warning()
ERROR | logger.error()
           | logger.exception()
CRITICAL | logger.critical()
```

## Writing and running tests ##

To write tests, built-in Unittest module is used.

To run tests, run (instead of an asterisk, substitute name of test)

```cmd
pipenv run python -v ./tests/test_*.py
```

## Contacts ##

[Telegram](https://t.me/+xfohB6gWiOU5YTUy) - Developer contact group.

[Slack](moreliatalk.slack.com) - an additional channel for communicating with developers.

## License ##

Copyright (c) 2020 - present MoreliaTalk team
  [NekrodNIK](https://github.com/NekrodNIK),
  [Stepan Skriabin](https://github.com/stepanskryabin),
  [rus-ai](https://github .com/rus-ai) and others.
  See full list in AUTHORS.md file.

Morelia Server is licensed under GNU Lesser General Public License version 3 or later (LGPL-3.0-or-later). See COPYING.LESSER file for details.
