"""
    Copyright (c) 2020 - present NekrodNIK, Stepan Skriabin, rus-ai and other.
    Look at the file AUTHORS.md(located at the root of the project) to get the
    full list.

    This file is part of Morelia Server.

    Morelia Server is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Morelia Server is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with Morelia Server. If not, see <https://www.gnu.org/licenses/>.
"""
from time import time
import json
import secrets
from collections import namedtuple

from mod.db.dbhandler import DBHandler
from mod.protocol.mtp.worker import MTProtocol
from mod.protocol.matrix.worker import MatrixProtocol


class MainHandler:
    def __init__(self,
                 request,
                 database: DBHandler,
                 protocol: str = 'mtp') -> None:
        self.request = request
        self.database = database
        self.protocol = protocol

        if protocol == 'matrix':
            self.response = self.matrix_handler()
        else:
            self.response = self.mtp_handler()

    def get_response(self):
        return self.response

    def mtp_handler(self) -> json:
        result = MTProtocol(self.request,
                            self.database).get_response()
        return result

    def matrix_handler(self) -> json:
        result = MatrixProtocol(self.request,
                                self.database).get_response()
        return result


class Clients:

    def __init__(self,
                 scope = None) -> None:
        self._scope = scope
        self.clients = []
        self.picker()
        self.time_to_live = 600 # second

    def picker(self) -> None:
        Client = namedtuple("Client", ["id",
                                       "scope",
                                       "add_time"])
        new_id = secrets.token_hex(32)
        new_client = Client(id=new_id,
                            scope=self._scope,
                            add_time=time())
        self.clients.extend(new_client)

    def get_silent_client(self) -> tuple:
        _clients = []
        for client in self.clients:
            if client.add_time < time() + self.time_to_live:
                client_index = self.clients.index(client)
            _clients.extend(self.clients[client_index])
        return tuple(_clients)

    def delete_client(self,
                      client):
        pass