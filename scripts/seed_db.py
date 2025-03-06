from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()
client = MongoClient('mongodb://localhost:27017')
db = client['mydatabase']
collection = db['mycollection']
document = {"name": "ars", "age": 20}
result = collection.insert_one(document)
print(f"Документ вставлен с ID: {result.inserted_id}")
client.close()
