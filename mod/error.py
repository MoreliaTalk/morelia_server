"""
    Copyright (c) 2020 - present NekrodNIK, Stepan Scryabin, rus-ai and other.
    Look at the file AUTHORS.md(located at the root of the project) to get the full list.

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

DICT: dict = {
            200: {
                'status': 'OK',
                'detail': 'successfully'
                },
            201: {
                'status': 'Created',
                'detail': 'Created'
                },
            202: {
                'status': 'Accepted',
                'detail': 'Accepted'
                },
            206: {
                'status': "Partial Content",
                'detail': "Partial Content"
                },
            400: {
                'status': 'Bad Request',
                'detail': 'Bad Request'
                },
            401: {
                'status': 'Unauthorized',
                'detail': 'Unauthorized'
                },
            403: {
                'status': 'Forbidden',
                'detail': 'Forbidden'
                },
            404: {
                'status': 'Not Found',
                'detail': 'Not Found'
                },
            405: {
                'status': 'Method Not Allowed',
                'detail': 'Method Not Allowed'
                },
            408: {
                'status': 'Request Timeout',
                'detail': 'Request Timeout'
                },
            409: {
                'status': 'Conflict',
                'detail': 'Such user (flow) is already on the server.'
                },
            415: {
                'status': 'Unsupported Media Type',
                'detail': 'Unsupported Media Type'
                },
            417: {
                'status': 'Expectation Failed',
                'detail': 'Expectation Failed'
                },
            426: {
                'status': 'Upgrade Required',
                'detail': 'Upgrade Required'
                },
            429: {
                'status': 'Too Many Requests',
                'detail': 'Too Many Requests'
                },
            499: {
                'status': 'Client Closed Request',
                'detail': 'Client Closed Request'
                },
            500: {
                'status': 'Internal Server Error',
                'detail': 'Internal Server Error'
                },
            503: {
                'status': 'Service Unavailable',
                'detail': 'Service Unavailable'
                },
            520: {
                'status': 'Unknown Error',
                'detail': 'Unknown Error'
            },
            526: {
                'status': 'Invalid SSL Certificate',
                'detail': 'Invalid SSL Certificate'
                },
            }
