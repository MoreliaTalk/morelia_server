# Morelia Server - server for MoreliaTalk messenger #


![tests](https://github.com/MoreliaTalk/morelia_server/workflows/Test%20and%20Linting/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/MoreliaTalk/morelia_server/badge.svg?branch=develop-nekrod)](https://coveralls.io/github/MoreliaTalk/morelia_server)

Language [EN](./README_ENG.md), [RU](./README.md)

## There are 2 branches in the repository ##

[Master](https://github.com/MoreliaTalk/morelia_server/tree/master) - stable branch.

## Applied in development ##

* [Python 3.10](https://www.python.org/) - programming language

* [Starlette](https://www.starlette.io/) - main framework

* [SQLObject](http://sqlobject.org) - ORM for working with the database

* [Pydantic](https://pydantic-docs.helpmanual.io) - data validation

* [Starlette](https://www.starlette.io) - lightweight ASGI framework/toolkit

* [websockets](https://pypi.org/project/websockets/) - implementation of the Websockets protocol in Python (RFC 6455 & 7692)

## Repository description ##

*/mod
  */config
    * config.py - the module is responsible for working with the config.ini configuration file
    * validator.py - module for validating the configuration file
  */db
    * dbhandler.py - the module is designed to execute queries to the database
    * models.py - the module is responsible for describing the database tables for working through the ORM.
  * /protocol
    */matrix
      * api.py - the module is responsible for the description of the API, as well as data validation.
      * worker.py - protocol implementation
    * /mtp
      * api.py - the module is responsible for the description of the API, as well as data validation.
      * worker.py - the module is responsible for implementing the methods described in the [Morelia Protocol](https://github.com/MoreliaTalk/morelia_protocol/blob/master/README.md).
    * error.py - the module is responsible for checking and generating responses with error codes.
    * controller.py - the module processes the request according to the protocol type
    * lib.py - the module is responsible for hashing the password, comparing the password with its hash sum, creating a hash for auth_id.
    * log_handler.py - logging configuration module.
    * config.py - module reads settings from config.ini
* server.py - main server code
* manage.py - cli tool for working with the server (launch, test client, work with the database, etc.)
* /tests
  * fixtures/ - json files with pre-prepared data for testing.
  * config.ini - server config for testing
  * test_*.py - tests
* example_config.ini - a file containing an example of server settings, just rename or copy to `config.ini` before starting the server.

## Installation ##

Install [Python](https://www.python.org/downloads/) version 3.10 or higher.

Download and install the latest version of [git](https://git-scm.com/downloads).

If you need a GUI, install [GitHub Desktop](https://desktop.github.com/).

Set up Git or GitHub Desktop by entering your `username` and `email` from the account created on [github](https://www.github.com).

## Fork of the Morelia Server repository ##

If you are not included in the team on the GitHub of the project, then you must first fork the Morelia Server repository to yourself by following [link] (https://github.com/MoreliaTalk/morelia_server/fork).

## Clone the repository on the local machine ##

Clone the repository to your local computer using the command line and `git`

```cmd
git clone https://github.com/{username}/morelia_server.git
cd morelia_server
```

Synchronize your fork with the original `upstream` Morelia Server repository

```cmd
git remote add upstream https://github.com/MoreliaTalk/morelia_server.git
```

Checking if the `upstream` repository appears in the list of remote repositories

```cmd
git remote -v
> origin https://github.com/{username}/morelia_server.git (fetch)
> origin https://github.com/{username}/morelia_server.git (push)
> upstream https://github.com/MoreliaTalk/morelia_server.git (fetch)
> upstream https://github.com/MoreliaTalk/morelia_server.git (push)
```

When using `GitHub`, select `Clone repository...` from the `File` menu, then follow the instructions

## Set up the Pipenv virtual environment ##

To work with the project, you need to install the libraries that it uses and configure the so-called. `virtual desktop` or `virtualenv`, for this use the [Pipenv] utility (https://github.com/pypa/pipenv)

If pipenv is not installed, run

```cmd
python -m pip install pipenv
```

Create a virtual environment in the project directory

```cmd
pipenv shell
```

Install all required libraries from Pipfile

```cmd
pipenv install --ignore-pipfile
```

## Before starting the server - use the settings manager ##

Before starting the server, you need to make some settings (create a database, tables and add the first user - administrator)

Open the `example_config.ini` file, find the URI parameter, replace it with the database path, example:
`URI = 'sqlite:db_sqlite.db' `, save the file as `config.ini`

Create a database with empty tables:

```cmd
pipenv run python