import os
import certifi

from mongoengine import connect

# mongo config
MONGO_DBNAME = os.environ.get("MONGO_DBNAME")
MONGO_CONNECT_URI = os.environ.get("MONGO_CONNECT_URI")

dbHandler = None


def connect_db():

    global dbHandler

    # Check is connected and active
    try:
        if dbHandler and dbHandler.server_info():
            return

    except Exception:
        pass

    dbHandler = connect(
        db=MONGO_DBNAME, host=MONGO_CONNECT_URI, tlsCAFile=certifi.where()
    )
