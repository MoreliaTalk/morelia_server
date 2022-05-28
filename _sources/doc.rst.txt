Documentation
*************

.. _doc:

Server
======

Server.py contains two function: ``server.home_page()`` processing server information output, and ``server.websocket_endpoint()``
responds connections for clients.

.. TODO: Should need to add description for server.py


MTP protocol
============

Read fully description about stable version of **MTP** protocol to this `link <https://github.com/MoreliaTalk/morelia_protocol>`_.

To work with MTP protocol server used ``protocol.mtp`` module which included these classes:

* MTPErrorResponse

* MTProtocol

* Response

* Request


MTPErrorResponse
----------------

Return response object with validation:

.. autoclass:: mod.protocol.mtp.worker.MTPErrorResponse
   :members:
   :private-members:
   :undoc-members:


MTProtocol
----------

Processing all methods contains MTP protocol description:

.. autoclass:: mod.protocol.mtp.worker.MTProtocol
   :members:
   :private-members:
   :undoc-members:


Validations Response
--------------------

Processing results of MTPProtocol methods with following validation and generate
response in JSON format:

.. autoclass:: mod.protocol.mtp.api.Response
   :members: data, errors, type, jsonapi, meta
   :no-private-members:
   :no-special-members:
   :undoc-members:


Validations Request
--------------------

Processing response received from clients with following validation and generate
error code when response not corresponds protocol methods:

.. autoclass:: mod.protocol.mtp.api.Request
   :members: data, errors, type, jsonapi, meta
   :no-private-members:
   :no-special-members:
   :undoc-members:


Matrix protocol
===============

Read fully description about latest version of **Matrix** protocol to `this <https://spec.matrix.org/latest/>`_ link.


MatrixProtocol
--------------

Processing half methods contains Matrix protocol description:

.. autoclass:: mod.protocol.matrix.worker.MatrixProtocol
   :members:
   :private-members:
   :undoc-members:


Validations Response
--------------------

Processing results of MatrixProtocol methods with following validation and generate
response in JSON format:



Validations Request
--------------------

Processing response received from clients with following validation and generate
error code when response not corresponds protocol methods:



Database
========


DBhandler
---------

High layer class has to work with database without query in raw SQL:

.. autoclass:: mod.db.dbhandler.DBHandler
   :members:
   :private-members:
   :undoc-members:


Models
------


UserConfig
++++++++++

UserConfig table where saving user secure and personal information:

.. autoclass:: mod.db.models.UserConfig


Flow
++++

Flow table where saving flow information:

.. autoclass:: mod.db.models.Flow


Message
+++++++

Message table where saving message information:

.. autoclass:: mod.db.models.Message


Admin
+++++

Admin table where saving access rights for web administration panel:

.. autoclass:: mod.db.models.Admin


Controller
==========


MainHandler
-----------

Class identifies and redirects requests with accordance type of protocol:

.. autoclass:: mod.controller.MainHandler
   :members:
   :private-members:
   :undoc-members:


Error
=====

Contains several new error code which additional for standard HTTP error code:

.. autoclass:: mod.error.ServerStatus


Checking matching status code name and type of errors contains in class ``mod.error.ServerStatus`` or ``HTTPStatus``

.. autofunction:: mod.error.check_error_pattern


Additional module
=================

Admin
-------

``admin``

.. autofunction:: admin.general.index_admin
.. autofunction:: admin.general.login_admin
.. autofunction:: admin.general.manage_admin
.. autofunction:: admin.general.manage_logs
.. autofunction:: admin.general.status_admin
.. autoexception:: admin.login.NotAuthenticatedException
.. autofunction:: admin.general.not_login_exception_handler
.. autofunction:: admin.login.get_admin_user_data
.. autofunction:: admin.login.login_token
.. autofunction:: admin.login.logout
.. autofunction:: admin.control.delete_user
.. autofunction:: admin.logs.get_logs
.. autofunction:: admin.logs.loguru_handler


Config
------

Module for working with the configuration file. Allows you to read and save the basic parameters
to the settings file in the root directory of the project:

.. autoclass:: mod.config.config.ConfigHandler
   :members:
   :private-members:
   :undoc-members:


.. autoexception:: mod.config.config.NameConfigError
   :members:
   :private-members:
   :undoc-members:


.. autoexception:: mod.config.config.BackupConfigError
   :members:
   :private-members:
   :undoc-members:


.. autoexception:: mod.config.config.OperationConfigError
   :members:
   :private-members:
   :undoc-members:


.. autoexception:: mod.config.config.AccessConfigError
   :members:
   :private-members:
   :undoc-members:


.. autoexception:: mod.config.config.RebuildConfigError
   :members:
   :private-members:
   :undoc-members:


.. autoexception:: mod.config.config.CopyConfigError
   :members:
   :private-members:
   :undoc-members:


.. autoclass:: mod.config.validator.ConfigModel
   :members: debug, debug_expiration_date, error, expiration_date, folder, info, level, max_version, messages, min_version, secret_key, size_auth_id, size_password, uri, users, uvicorn_logging_disable
   :private-members:
   :undoc-members:

Hash
----

Generating a hash for a password or session.
Password hash verification.
Generating a user authentication token.

.. autoclass:: mod.lib.Hash
   :members:
   :private-members:
   :undoc-members:


Logging
-------

Adding and configuring project logging.

.. autofunction:: mod.log_handler.add_logging