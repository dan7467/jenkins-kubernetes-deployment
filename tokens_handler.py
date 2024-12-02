import os

credentials = {
    
    "mongo": {"db_name": os.environ['mongo_dbname'], "user_name": os.environ['mongo_user'], "user_pass": os.environ['mongo_pass']},
    "mailjet": {"secret_key": os.environ['mailjet_secret_key'], "api_key": os.environ['mailjet_api_key']},
    "theirstack": {"api_key": os.environ['theirstack_token']}
    
}


def get_credentials(needed_service):
    return credentials[needed_service]