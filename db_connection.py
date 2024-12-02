# import redis

# # Redis configuration
# redis_client = redis.StrictRedis(
#     host='localhost',
#     port=6379,
#     decode_responses=True
# )

from pymongo import MongoClient
from secret_handler import get_credentials

credentials = get_credentials('mongo')

mongo_client = MongoClient(f"mongodb+srv://{credentials['user_name']}:{credentials['user_pass']}@cluster0.ikhzv.mongodb.net/?retryWrites=true&w=majority")

db = mongo_client[credentials['db_name']]