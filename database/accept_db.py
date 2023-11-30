
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from threading import RLock
from info import DATABASE_NAME, DATABASE_URI, LOGGER

DB_NAME = DATABASE_NAME
DB_URI = DATABASE_URI
INSERTION_LOCK = RLock()

try:
    alita_db_client = MongoClient(DB_URI)
except PyMongoError as f:
    LOGGER.error(f"Error in Mongodb: {f}")
    exiter(1)
alita_main_db = alita_db_client[DB_NAME]


class MongoDB:
    """Class for interacting with Bot database."""

    def __init__(self, collection) -> None:
        self.collection = alita_main_db[collection]

    # Insert one entry into collection
    def insert_one(self, document):
        result = self.collection.insert_one(document)
        return repr(result.inserted_id)

    # Find one entry from collection
    def find_one(self, query):
        result = self.collection.find_one(query)
        if result:
            return result
        return False

    # Find entries from collection
    def find_all(self, query=None):
        if query is None:
            query = {}
        return list(self.collection.find(query))

    # Count entries from collection
    def count(self, query=None):
        if query is None:
            query = {}
        return self.collection.count_documents(query)

    # Delete entry/entries from collection
    def delete_one(self, query):
        self.collection.delete_many(query)
        return self.collection.count_documents({})

    # Replace one entry in collection
    def replace(self, query, new_data):
        old = self.collection.find_one(query)
        _id = old["_id"]
        self.collection.replace_one({"_id": _id}, new_data)
        new = self.collection.find_one({"_id": _id})
        return old, new

    # Update one entry from collection
    def update(self, query, update):
        result = self.collection.update_one(query, {"$set": update})
        new_document = self.collection.find_one(query)
        return result.modified_count, new_document

    @staticmethod
    def close():
        return alita_db_client.close()


def __connect_first():
    _ = MongoDB("test")
    LOGGER.info("Initialized Database!\n")


__connect_first()

class Accept(MongoDB):
    database_name = "auto_accept"

    def __init__(self, chat_id: int) -> None:
        super().__init__(self.database_name)
        self.chat_id = chat_id
        self.chat_info = self.__ensure_in_db()
      
    def get_accept_status(self):
        with INSERTION_LOCK:
            return self.chat_info["autoaccept"]
            
    def set_current_accept_settings(self, status: bool):
        with INSERTION_LOCK:
            return self.update({"_id": self.chat_id}, {"autoaccept": status})
 
    def __ensure_in_db(self):
        chat_data = self.find_one({"_id": self.chat_id})
        if not chat_data:
            new_data = {
                "_id": self.chat_id,
                "autoaccept": False
            }
            self.insert_one(new_data)
            LOGGER.info(f"Initialized acceptor Document for chat {self.chat_id}")
            return new_data
        return chat_data
