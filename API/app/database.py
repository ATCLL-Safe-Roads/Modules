from pymongo import mongo_client
import pymongo
from app.config import settings

client = mongo_client.MongoClient(settings.DATABASE_URL)
print('Connected to MongoDB...')

db = client[settings.MONGO_INITDB_DATABASE]

# Add Here The Collections and The Constraints

Event = db.events
Flow = db.flows

Event.create_index([("id", pymongo.ASCENDING)], unique=True)
Flow.create_index([("id", pymongo.ASCENDING)], unique=True)