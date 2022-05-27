Install and Run
***************


Install
-------

.. _installation:

* Install `Python <https://www.python.org/downloads/>`_ version 3.10 or higher.

* Download and install the latest version `git <https://git-scm.com/downloads>`_.

* If you need a GUI, install `GitHub Desktop <https://desktop.github.com/>`_.

* Set up Git or GitHub Desktop by entering your ``username`` and ``email`` from an account created on `github <https://www.github.com>`_.


Configuring the Pipenv
----------------------

To work with the project it is necessary to install the libraries that it uses and configure the so-called
`virtual environment` or `virtualenv`, for this purpose the utility `Pipenv <https://github.com/pypa/pipenv>`_

1. If pipenv is not installed, run:

::

 python -m pip install pipenv

2. Create a virtual environment in project directory:

::

 pipenv shell

3. Install all required libraries from Pipfile:

::

 pipenv install --ignore-pipfile


Before starting the server
--------------------------

Before you start the server you need to make some settings (create a database, tables and add the first user - administrator)

1. Create a database with empty tables:

::

 pipenv run python ./manage.py db create


2. If you want to delete all tables in the created database (**WARNING** only tables are deleted, the database is not deleted):

::

 pipenv run python ./manage.py db delete


3. Add the administrator in the created database:

::

 pipenv run python ./manage.py db admin-create


4. Additionally, you can create a ``flow`` or ``user``:

::

 pipenv run python ./manage.py db flow-create
 pipenv run python ./manage.py db user-create


5. Information about all the features of the configuration manager:

::

 pipenv run python ./manage.py --help


Server startup
--------------

To start server, use command:

::

 pipenv run python ./manage.py runserver


Parameters that can be sent to server:
--host, -h <str>            IP address, default `localhost`
--port, -p <str>            Port for server, default 8000
--log-level <str>           Set the log level. Options: **critical**, **error**, **warning**, **info**, **debug**, **trace**.
                            Default: **info**.
--use-colors                Enable colorized formatting of the log records, in case this is not set it will be auto-detected.
--reload, -r                Enable auto-reload. Uvicorn supports two versions of auto-reloading behavior enabled by this option.
                            There are important differences between them.


Working with built-in client
----------------------------

To test the server, you can send a test message using the built-in mini client, for which you must use the key "-t" to pass the type of message from the options:
``register_user``, ``get_update``, ``send_message``, ``all_messages``, ``add_flow``, ``all_flow``, ``user_info``, ``authentication``, ``delete_user``, ``delete_message``,
``edited_message``, ``ping_pong``, ``error``.

::

 pipenv run python ./manage.py testclient send -t register_user
