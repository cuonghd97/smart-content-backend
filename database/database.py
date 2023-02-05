from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

class MongoConnection:
    @staticmethod
    def get_connection_mongo() -> any:
        return MongoClient(host="mongodb://localhost:27017")
    
    def get_database(self) -> Database:
        return self.get_connection_mongo().get_database(
            "smartContent"
        )
    def get_collection(self, collection_name) -> Collection:
        return self.get_database().get_collection(collection_name)