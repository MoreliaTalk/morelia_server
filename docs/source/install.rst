Install and Run
***************


Install
-------

.. _installation:

* Install `Python <https://www.python.org/downloads/>`_ version 3.8 or higher.

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

 pipenv run python ./manage.py --db create


2. If you want to delete all tables in the created database (**WARNING** only tables are deleted, the database is not deleted):

::

 pipenv run python ./manage.py --db delete


3. Add the administrator in the created database:

::

 pipenv run python ./manage.py --table superuser


4. Additionally, you can create a ``flow`` with the group type:

::

 pipenv run python ./manage.py --table flow


5. Information about all the features of the configuration manager:

::

 pipenv run python ./manage.py --help


Server startup
--------------

To start server, use command:

::

 uvicorn server:app --host 0.0.0.0 --port 8000 --reload --use-colors --http h11 --ws websockets


Additional parameters that can be sent to server:

--log-level <str>           Set the log level. Options: **critical**, **error**, **warning**, **info**, **debug**, **trace**.
                            Default: **info**.
--use-colors                Enable colorized formatting of the log records, in case this is not set it will be auto-detected.
                            This option is ignored if the ``--log-config`` CLI option is used.
--no-use-colors             Disable colorized formatting of the log records.
--loop <str>                Set the event loop implementation. The uvloop implementation provides greater performance,
                            but is not compatible with Windows or PyPy. Options: **auto**, **asyncio**, **uvloop**.
                            Default: **auto**.
--http <str>                Set the HTTP protocol implementation. The httptools implementation provides greater performance,
                            but it is not compatible with PyPy, and requires compilation on Windows.
                            Options: **auto**, **h11**, **httptools**. Default: **auto**.
--ws <str>                  Set the WebSockets protocol implementation. Either of the websockets and wsproto packages are
                            supported. Use **none** to deny all websocket requests. Options: **auto**, **none**, **websockets**,
                            **wsproto**. Default: **auto**.
--lifespan <str>            Set the Lifespan protocol implementation. Options: **auto**, **on**, **off**. Default: **auto**.
--interface                 Select ASGI3, ASGI2, or WSGI as the application interface. Note that WSGI mode always disables
                            WebSocket support, as it is not supported by the WSGI interface.
                            Options: **auto**, **asgi3**, **asgi2**, **wsgi**. Default: **auto**.
--limit-concurrency <int>   Maximum number of concurrent connections or tasks to allow, before issuing HTTP 503 responses.
                            Useful for ensuring known memory usage patterns even under over-resourced loads.
--limit-max-requests <int>  Maximum number of requests to service before terminating the process.
                            Useful when running together with a process manager, for preventing memory leaks from impacting
                            long-running processes.
--backlog <int>             Maximum number of connections to hold in backlog. Relevant for heavy incoming traffic.
                            Default: **2048**
--ssl-keyfile <path>        SSL key file
--ssl-certfile <path>       SSL certificate file
--ssl-version <int>         SSL version to use (see stdlib ssl module's)
--ssl-cert-reqs <int>       Whether client certificate is required (see stdlib ssl module's)
--ssl-ca-certs <str>        CA certificates file
--ssl-ciphers <str>         Ciphers to use (see stdlib ssl module's)
--timeout-keep-alive <int>  Close Keep-Alive connections if no new data is received within this timeout. Default: 5.


**DEBUG** mode
--------------

To easily start the server in debug mode, all you need to do is run `debug_server.py`:

::

 pipenv run python ./debug_server.py


Working with built-in client
----------------------------

To test the server, run the mini client ``client.py`` in the console:

::

 pipenv run python -i ./client.py


After launching, the client will send an authorization message (AUTH) to the server, the server's response will be displayed
in the console, after which ``python`` will go into interactive line mode ``>>>``, so that it is possible to perform additional checks.

In the interactive console, there will be one function available to send ``end_message`` which takes two arguments
``message`` message and ``uri`` server address. In the argument ``message`` you need to pass an object with type *"dict"*
or *"str"*, you can use ready-made examples of queries: **AUTH**, **GET_UPDATE**, **ADD_FLOW**, **ALL_FLOW**.
In the argument you must pass an object with type *"str"*, you can use ready examples of server address: **LOCALHOST**.

::

 >>> send_message(GET_UPDATE, LOCALHOST)


If no arguments are passed to the function, the default is to send an **AUTH** message to **LOCALHOST**.
