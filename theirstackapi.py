import requests
from tokens_handler import get_credentials

url = "https://api.theirstack.com/v1/jobs/search"

querystring = {"token": get_credentials('theirstack')['api_key']}

# TO-DO: extend the search engine

def get_payload(free_text = "", page = 0, limit = 1, job_country_or_code = ["US"], posted_at_max_age_days = 7, optional_params = {}):
    
    payload = {
        "page": page,
        "limit": limit,
        "job_country_code_or": job_country_or_code,
        "posted_at_max_age_days": posted_at_max_age_days
    }   
    
    for param_key, param_val in optional_params.items():
        
        payload[param_key] = param_val
    
    if free_text == "":
        
        return requests.post(url, json=payload, params=querystring).json()['data']
    
    payload['job_title_pattern_and'] = free_text.split(' ')
    
    return requests.post(url, json=payload, params=querystring).json()['data']
    