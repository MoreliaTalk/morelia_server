Development
***********

.. _development:


Git repository
--------------

Main branch `master <https://github.com/MoreliaTalk/morelia_server/tree/master>`_


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

2. Switching to ``master`` branch:

::

 git checkout master

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


Running before create pull-request
__________________________________

Before create pull-request you must be perform three steps:

1. Running static type checker ``mypy``:

::

 pipenv run mypy --config=./setup.cfg .


2. Running ``flake8`` for checking code:

::

 pipenv run flake8 --config ./setup.cfg --show-source --statistics --output-file ./log/flake8.log

``--config ./setup.cfg`` - path to flake8 settings

``--show-source`` - show the source generate each error or warning

``--statistics`` - count errors and warnings

``--output-file ./log/flake8.log`` - path to file where flake8 saved all information about occurrences errors and warnings

3. Running unittest for testing code (``tests`` it's a directory contains all test for project):

::

 pipenv run coverage run -m unittest discover tests


Creating a pull-request
-----------------------

For making changes to development branch Morelia Server.

1. Getting the latest changes from development branch Morelia Server:

::

 git pull upstream master


2. Sending changes to main branch of your fork:

::

 git push


3. To create a pull-request, you need to go to `GitHub <https://www.github.com>`_, select your fork and click on
``New pull request`` in right-hand menu, then select branch from which you want to push changes to Morelia Server
master branch and click ``Create pull request``.


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



Repository description
----------------------

``/admin/templates`` - templates of admin pages

``/admin/general.py`` - 

``/admin/control.py`` - 

``/admin/login.py`` - 

``/admin/logs.py`` - 

``/mod/db/dbhandler.py`` - module is designed to perform queries to the database

``/mod/db/models.py`` - module is responsible for the description of database tables to work through OPM

``/mod/protocol/matrix/api.py`` - module is responsible for the description of API, as well as the validation of data.

``/mod/protocol/matrix/worker.py`` - implementation of the protocol

``/mod/protocol/mtp/api.py`` - module responsible for API description, as well as data validation.

``/mod/protocol/worker.py`` - module is responsible for implementing the methods described in `Morelia Protocol <https://github.com/MoreliaTalk/morelia_protocol/blob/master/README.md>`_.

``/mod/error.py`` - module is responsible for checking and generating responses with error codes.

``/mod/controller.py`` - module is responsible for processing requests according to the protocol type.

``/mod/lib.py`` - module is responsible for password hashing, comparing password with its hash sum, creating hash for ``auth_id``.

``/mod/log_handler.py`` - module configures logging.

``/mod/config/config.py`` - module reads settings from config.ini

``/mod/config/validator`` - data validation for config.ini

``/static/`` - static files

``/server.py`` - main server code

``/manage.py`` - database migration manager (creating and deleting database tables), mnanage database, create and delete admin, user and flow. Running server and run mini test client.

``/tests/fixtures/`` - json-files with preliminarily prepared data for tests

``/tests/fixtures/config.ini`` - server config for the tests

``/tests/test_*.py`` - tests

``/example_config.ini`` - file containing example server settings, just rename it to ``config.ini`` before running the server.
