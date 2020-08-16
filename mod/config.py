import os

# Configuring database access
# SQLite3
LOCAL_SQLITE = ''.join(['sqlite:', os.path.abspath('db_sqlite.db')])

# Local PostgreSQL
LOCAL_POSTGRESQL = 'postgres://testdb:123456@127.0.0.1/test_morelia_server'

# Online PostgreSQL
ONLINE_POSTGRESQL = os.getenv('DATABASE_URL')

# Version of Morelia Protocol
API_VERSION = '1.0'

# LibHash config #
# TODO
# add constat for configurating iteration cycle

# size of output hash digest in bytes
PASSWORD_HASH_SIZE = 32

# size of output auth_id digest in bytes
AUTH_ID_HASH_SIZE = 16

# Settings uvicorn
UVICORN_HOST = "0.0.0.0"

UVICORN_PORT = 8000

# Settings Jinja2

TEMPLATE_FOLDER = 'templates'
