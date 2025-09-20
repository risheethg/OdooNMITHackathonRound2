from pymongo import MongoClient
from pymongo.database import Database

from .config import settings

class DBConnection:
    """
    Manages the connection to the MongoDB database.
    This class ensures that there is only one client instance created.
    """
    _client: MongoClient | None = None

    def __init__(self):
        # Establish connection to MongoDB using the URI from settings.
        if DBConnection._client is None:
            DBConnection._client = MongoClient(settings.MONGO_URI)

    def get_database(self) -> Database:
        """
        Returns the database instance specified in the settings.

        Returns:
            Database: The PyMongo database object.
        """
        if DBConnection._client is None:
            # This should not happen if initialized properly, but it's a safeguard.
            self.__init__()
        
        # This is guaranteed to not be None because of the check above.
        client = DBConnection._client
        return client[settings.MONGO_DB_NAME]

# Instantiate the connection manager.
db_connection = DBConnection()

# A simple function to be used as a FastAPI dependency to get the DB instance.
def get_db() -> Database:
    """
    Returns a database instance from the connection manager.
    """
    return db_connection.get_database()
