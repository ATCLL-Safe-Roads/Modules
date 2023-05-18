import pymongo

from app.config import settings

client = pymongo.mongo_client.MongoClient(settings.DATABASE_URL)

db = client[settings.MONGO_DATABASE]

Event = db.events
Flow = db.flows

print('INFO: Connected to MongoDB.')
