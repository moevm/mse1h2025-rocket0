from requests import sessions
from pprint import pprint
from rocketchat_API.rocketchat import RocketChat
from dotenv import load_dotenv
import os
from pymongo import MongoClient

load_dotenv()
client = MongoClient('mongodb://localhost:27017')
db = client['mydatabase']
collection = db['mycollection']
document = {"name": "ars", "age": 20}
result = collection.insert_one(document)
print(f"Документ вставлен с ID: {result.inserted_id}")
client.close()
