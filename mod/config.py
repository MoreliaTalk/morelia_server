import os

# Configuring database access
# SQLite3
LOCAL_SQLITE: str = ''.join(['sqlite:', os.path.abspath('db_sqlite.db')])

# Local PostgreSQL
LOCAL_POSTGRESQL: str = 'postgres://postgres:123456@127.0.0.1/morelia_server_db?debug=True'

# Online PostgreSQL
ONLINE_POSTGRESQL: str = os.getenv('DATABASE_URL')

# Version of Morelia Protocol
API_VERSION: str = '1.0'

# LibHash config #
# TODO
# add constat for configurating iteration cycle

# size of output hash digest in bytes
PASSWORD_HASH_SIZE: int = 32

# size of output auth_id digest in bytes
AUTH_ID_HASH_SIZE: int = 16

# Settings loguru
DEBUG_LEVEL: int = 10

# Settings Jinja2
TEMPLATE_FOLDER: str = 'templates'

# Setting up number of messages that server gives out on
# "get_all_message" client request
LIMIT_MESSAGE: int = 100

# Status and error description settings, where
# "status" - corresponds to the same status for HTTP error codes
# "detail" - description of the error, understandable for humans
DICT_ERRORS: dict = {
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
