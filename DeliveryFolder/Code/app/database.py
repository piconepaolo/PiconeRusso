from pymongo import MongoClient

from app.core import config

mongo_client: MongoClient = MongoClient(config.db.connection_url)
