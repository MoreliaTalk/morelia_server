from mod import controller
from mod import config
import sqlobject as orm
import json

connection = orm.connectionForURI(config.LOCAL_SQLITE)
orm.sqlhub.processConnection = connection

a = controller.ProtocolMethods(
    json.dumps(
        {
            "type": "register_user",
            "data": {
                "user": {
                    "password": "password",
                    "login": "login",
                    "email": "querty@querty.com",
                    "username": "username"
                },
                "meta": None
            },
            "jsonapi": {
                "version": "1.0"
            },
            "meta": None
        }
    )
)
print(a.response_get())
