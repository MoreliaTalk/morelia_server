import sys

from mod.config import ConfigHandler
from mod.db.dbhandler import DBHandler

# Get parameters contains in config.ini
_config = ConfigHandler()
config_option = _config.read()

# Set database connection
if "unittest" in sys.modules:
    db_connect = DBHandler()
else:
    db_connect = DBHandler(uri=config_option.uri)
