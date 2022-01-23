Documentation
*************

.. _doc:

Server
======

Description about ``server.home_page()``

.. autofunction:: server.home_page

Description about ``server.websocket_endpoint()``

.. autofunction:: server.websocket_endpoint


MTP protocol
============

To work with MTP protocol used ``protocol.mtp`` module which included these classes:

* MTPErrorResponse

* MTProtocol

* Response

* Request


MTPErrorResponse
----------------

General description of the class ``mod.protocol.mtp.worker.MTPErrorResponse``:

.. autoclass:: mod.protocol.mtp.worker.MTPErrorResponse
   :members:
   :private-members:
   :undoc-members:


MTProtocol
----------

General description of the class ``mod.protocol.mtp.worker.MTProtocol``:

.. autoclass:: mod.protocol.mtp.worker.MTProtocol
   :members:
   :private-members:
   :undoc-members:


Validations Response
--------------------

General description of the class ``mod.protocol.mtp.api.Response``:

.. autoclass:: mod.protocol.mtp.api.Response
   :members: data, errors, type, jsonapi, meta
   :no-private-members:
   :no-special-members:
   :undoc-members:


Validations Request
--------------------

General description of the class ``mod.protocol.mtp.api.Request``:

.. autoclass:: mod.protocol.mtp.api.Request
   :members: data, errors, type, jsonapi, meta
   :no-private-members:
   :no-special-members:
   :undoc-members:


Matrix protocol
===============


MatrixProtocol
--------------

To work with the database, the **Models** class is designed, which implements methods of high-level interaction with the OPM.

General description of the class ``mod.protocol.matrix.worker.MatrixProtocol``:

.. autoclass:: mod.protocol.matrix.worker.MatrixProtocol
   :members:
   :private-members:
   :undoc-members:


Validations Response
--------------------

General description of the class ``mod.protocol.matrix.api.Response``:



Validations Request
--------------------

General description of the class ``mod.protocol.matrix.api.Request``:



Database
========


DBhandler
---------

To work with the database, the **DBHandler** class is designed, which implements methods of high-level interaction with the OPM.

General description of the class ``mod.db.dbhandler.DBHandler``:

.. autoclass:: mod.db.dbhandler.DBHandler
   :members:
   :private-members:
   :undoc-members:


Models
------


UserConfig
++++++++++

To work with the database, the **Models** class is designed, which implements methods of high-level interaction with the OPM.

General description of the class ``mod.db.models.UserConfig``:

.. autoclass:: mod.db.models.UserConfig


Flow
++++

To work with the database, the **Models** class is designed, which implements methods of high-level interaction with the OPM.

General description of the class ``mod.db.models.Flow``:

.. autoclass:: mod.db.models.Flow


Message
+++++++

To work with the database, the **Models** class is designed, which implements methods of high-level interaction with the OPM.

General description of the class ``mod.db.models.Message``:

.. autoclass:: mod.db.models.Message


Admin
+++++

To work with the database, the **Models** class is designed, which implements methods of high-level interaction with the OPM.

General description of the class ``mod.db.models.Admin``:

.. autoclass:: mod.db.models.Admin


Controller
==========


MainHandler
-----------

To work with the database, the **Models** class is designed, which implements methods of high-level interaction with the OPM.

General description of the class ``mod.controller.MainHandler``:

.. autoclass:: mod.controller.MainHandler
   :members:
   :private-members:
   :undoc-members:

Error
=====

To work with the database, the **Models** class is designed, which implements methods of high-level interaction with the OPM.

General description of the class ``mod.error.ServerStatus``:

.. autoclass:: mod.error.ServerStatus


.. autofunction:: mod.error.check_error_pattern


Additional module
=================

Hash
----

To work with the database, the **Models** class is designed, which implements methods of high-level interaction with the OPM.

General description of the class ``mod.lib.Hash``:

.. autoclass:: mod.lib.Hash
   :members:
   :private-members:
   :undoc-members:


Logging
-------

To work with the database, the **Models** class is designed, which implements methods of high-level interaction with the OPM.

General description of the class ``mod.logging.add_logging()``:

.. autofunction:: mod.logging.add_logging

