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

Class ``mod.protocol.mtp.worker.MTPErrorResponse`` return response object with validation:

.. autoclass:: mod.protocol.mtp.worker.MTPErrorResponse
   :members:
   :private-members:
   :undoc-members:


MTProtocol
----------

Class ``mod.protocol.mtp.worker.MTProtocol`` processing all methods contains MTP protocol description:

.. autoclass:: mod.protocol.mtp.worker.MTProtocol
   :members:
   :private-members:
   :undoc-members:


Validations Response
--------------------

Class ``mod.protocol.mtp.api.Response`` processing results of MTPProtocol methods with following validation and generate
response in JSON format:

.. autoclass:: mod.protocol.mtp.api.Response
   :members: data, errors, type, jsonapi, meta
   :no-private-members:
   :no-special-members:
   :undoc-members:


Validations Request
--------------------

General description of the class ``mod.protocol.mtp.api.Request`` processing response received from clients with following
validation and generate error code when response not corresponds protocol methods:

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

Class ``mod.protocol.matrix.worker.MatrixProtocol`` processing half methods contains Matrix protocol description:

.. autoclass:: mod.protocol.matrix.worker.MatrixProtocol
   :members:
   :private-members:
   :undoc-members:


Validations Response
--------------------

General description of the class ``mod.protocol.matrix.api.Response`` processing results of MatrixProtocol methods with
following validation and generate response in JSON format:



Validations Request
--------------------

General description of the class ``mod.protocol.matrix.api.Request`` processing response received from clients with following
validation and generate error code when response not corresponds protocol methods:



Database
========


DBhandler
---------

Class ``mod.db.dbhandler.DBHandler`` high layer class has to work with database without query in raw SQL:

.. autoclass:: mod.db.dbhandler.DBHandler
   :members:
   :private-members:
   :undoc-members:


Models
------


UserConfig
++++++++++

Description UserConfig table where saving user secure and personal information ``mod.db.models.UserConfig``:

.. autoclass:: mod.db.models.UserConfig


Flow
++++

Description Flow table where saving flow information ``mod.db.models.Flow``:

.. autoclass:: mod.db.models.Flow


Message
+++++++

Description Message table where saving message information ``mod.db.models.Message``:

.. autoclass:: mod.db.models.Message


Admin
+++++

Description Admin table where saving access rights for web administration panel ``mod.db.models.Admin``:

.. autoclass:: mod.db.models.Admin


Controller
==========


MainHandler
-----------

Class identifies and redirects requests with accordance type of protocol ``mod.controller.MainHandler``:

.. autoclass:: mod.controller.MainHandler
   :members:
   :private-members:
   :undoc-members:


Error
=====

Contains several new error code which additional for standard HTTP error code.

General description of the class ``mod.error.ServerStatus``:

.. autoclass:: mod.error.ServerStatus


Checking matching status code name and type of errors contains in class ``mod.error.ServerStatus`` or ``HTTPStatus``

.. autofunction:: mod.error.check_error_pattern


Additional module
=================

Hash
----

``mod.lib.Hash``:

.. autoclass:: mod.lib.Hash
   :members:
   :private-members:
   :undoc-members:


Logging
-------

``mod.logging.add_logging()``:

.. autofunction:: mod.logging.add_logging

