import os

# Configuring database access
# SQLite3
LOCAL_SQLITE = ''.join(['sqlite:', os.path.abspath('db_sqlite.db')])

# Local PostgreSQL
LOCAL_POSTGRESQL = 'postgres://testdb:123456@127.0.0.1/test_morelia_server'

# Online PostgreSQL
ONLINE_POSTGRESQL = os.getenv('DATABASE_URL')


API_VERSION = 1.0