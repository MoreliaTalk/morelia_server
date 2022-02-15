Development
***********

.. _development:


Git repository
--------------

Stable branch `master <https://github.com/MoreliaTalk/morelia_server/tree/master>`_

Branch to add new functionality `develop <https://github.com/MoreliaTalk/morelia_server/tree/develop>`_


Fork repository
---------------

.. _fork:

If you are not on the GitHub project team, you must first fork the Morelia Server repository to yourself by going to
`link <https://github.com/MoreliaTalk/morelia_server/fork>`_.


Cloning a repository
--------------------

1. Clone repository to your local computer using command line:

::

 git clone https://github.com/{username}/morelia_server.git
 cd morelia_server

2. Switching to ``develop`` branch:

::

 git checkout develop

3. Synchronizing your fork with original repository ``upstream`` Morelia Server:

::

 git remote add upstream https://github.com/MoreliaTalk/morelia_server.git


4. Check if repository ``upstream`` appeared in the list of deleted repositories:

::

 git remote -v
 > origin    https://github.com/{username}/morelia_server.git (fetch)
 > origin    https://github.com/{username}/morelia_server.git (push)
 > upstream  https://github.com/MoreliaTalk/morelia_server.git (fetch)
 > upstream  https://github.com/MoreliaTalk/morelia_server.git (push)


5. If using GitHub Desktop, select ``Clone repository...`` from ``File`` menu and follow instructions.


Creating a pool-request
-----------------------

For making changes to development branch Morelia Server.

1. Getting the latest changes from development branch Morelia Server:

::

 git pull upstream develop


2. Sending changes to development branch of your fork:

::

 git push


3. To create a pull-request, you need to go to `GitHub <https://www.github.com>`_, select your fork and click on
``New pull request`` in right-hand menu, then select branch from which you want to push changes to Morelia Server
development branch and click ``Create pull request``.


Code style requirements
-----------------------

Before starting work, it is recommended that you read:

* `PEP 8 - Python Code Writing Guide <https://pythonworld.ru/osnovy/pep-8-rukovodstvo-po-napisaniyu-koda-na-python.html>`_.

* `Google style of comment and docstring <https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings>`_

Be sure to use a linter (flake8, pylint or similar).


Writing and running tests
-------------------------

Built-in Unittest module is used to write tests.

To run tests, run (replace asterisk with test name):

::

 pipenv run python -v ./tests/test_*.py


Running the debugger
--------------------

To run debugger in a working server environment, through console

::

 python -m pdb ./debug_server.py


To get help in debug mode:

::

 (pdb) help


Repository description
----------------------

`/admin/templates` - templates of admin pages

`/admin/admin.py` - admin.py

`/admin/control.py` - control.py

`/admin/login.py` - login.py

`/admin/logs.py` - logs.py

`/mod/db/dbhandler.py` - module is designed to perform queries to the database

`/mod/db/models.py` - module is responsible for the description of database tables to work through OPM

`/mod/protocol/matrix/api.py` - module is responsible for the description of API, as well as the validation of data.

`/mod/protocol/matrix/worker.py` - implementation of the protocol

`/mod/protocol/mtp/api.py` - module responsible for API description, as well as data validation.

`/mod/protocol/worker.py` - module is responsible for implementing the methods described in `Morelia Protocol <https://github.com/MoreliaTalk/morelia_protocol/blob/master/README.md>`_.

`/mod/error.py` - module is responsible for checking and generating responses with error codes.

`/mod/controller.py` - module is responsible for processing requests according to the protocol type.

`/mod/lib.py` - module is responsible for password hashing, comparing password with its hash sum, creating hash for ``auth_id``.

`/mod/logging.py` - module configures logging.

`/config.py` - module reads settings from config.ini

`/static/` - static files

`/server.py` - main server code

`/manage.py` - database migration manager (creating and deleting database tables)

`/tests/fixtures/` - json-files with preliminarily prepared data for tests

`/tests/config.ini` - server config for the tests

`/tests/test_*.py` - tests

`/debug_server.py` - wrapper for server.py to debug through the ``pdb`` utility.

`/example_config.ini` - file containing example server settings, just rename it to ``config.ini`` before running the server.

`/client.py` - mini-customer to test the server.
