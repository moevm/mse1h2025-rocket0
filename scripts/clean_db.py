from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient('mongodb://localhost:27017')

database_names = client.list_database_names()

system_databases = ['admin', 'local', 'config']
database_names = [db for db in database_names if db not in system_databases]

for db_name in database_names:
    db = client[db_name]
    collection_names = db.list_collection_names()

    for collection_name in collection_names:
        collection = db[collection_name]

        result = collection.delete_many({})
        print(
            f"Удалено {result.deleted_count} документов из коллекции {collection_name} в базе данных {db_name}")

client.close()
