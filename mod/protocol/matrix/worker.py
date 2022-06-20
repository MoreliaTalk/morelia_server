"""
Copyright (c) 2021 - present NekrodNIK, Stepan Skriabin, rus-ai and other.
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


class MatrixProtocol:
    """
    Processing requests and forming response according to "Matrix" protocol.

    Read actual description of protocol:
    https://spec.matrix.org/v1.1/

    Args:
        request: JSON request from websocket client
        database (DBHandler): object - database connection point

    Returns:
        returns class api.Response
    """

    def __init__(self,
                 request: str,
                 database: DBHandler):
        self.request = request
        self._db = database

    @staticmethod
    def get_response() -> str:
        """
        Generates a JSON-object containing result of an instance json.

        Returns:
                (json): json-object which contains validated response

        """

        result = "Method not worked"
        return result
