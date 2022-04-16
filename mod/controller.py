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
from mod.db.dbhandler import DBHandler
from mod.protocol.matrix.worker import MatrixProtocol
from mod.protocol.mtp.worker import MTProtocol


class MainHandler:
    """
    According to the selected protocol sends a request to the handler.

    Args:
        request (object): JSON request from websocket client
        database (DBHandler): object - database connection point
        protocol (str): name of using protocol, 'mtp' or 'matrix'.
    """

    def __init__(self,
                 request,
                 database: DBHandler,
                 protocol: str = 'mtp') -> None:
        self.request = request
        self.database = database
        self.protocol = protocol

        if protocol == 'matrix':
            self.response = self._matrix_handler()
        else:
            self.response = self._mtp_handler()

    def get_response(self):
        """
        Returns result of request processing depending on the protocol.

        Returns:
            (str)
        """

        return self.response

    def _mtp_handler(self) -> str:
        """
        Returns result get_response method of the class handling MTP protocol.

        Returns:
            (str):
        """

        result = MTProtocol(self.request,
                            self.database).get_response()
        return result

    def _matrix_handler(self) -> str:
        """
        Returns result get_response method of class handling Matrix protocol.

        Returns:
            (str):
        """

        result = MatrixProtocol(self.request,
                                self.database).get_response()
        return result
