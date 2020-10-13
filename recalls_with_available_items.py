# This script doesn't need user input. You run it, it gets data from FOLIO, it prints the results to a file prefedined file/file location. 

#TODO Refine which available items to return -- are e.g. items with loantype Reference

import json
import time
from datetime import datetime
import re
import requests
from requests.exceptions import HTTPError

# Import some local variables from a separate .py file
import authlocal as auth

# Define a function that sets base url and headers for API requests
def set_local_variables():
    local_variables = {
        'baseurl' : auth.okapiUrl,
        'headers' : {'x-okapi-tenant': auth.xOkapiTenant, 'x-okapi-token': auth.xOkapiToken}
    }
    return local_variables

# Define a function that makes a GET request with a query
def make_get_request_w_query_and_limit(endpoint, query, limit):
    local_variables = set_local_variables()

    baseurl = local_variables['baseurl']
    headers = local_variables['headers']
    params = {'format': 'json'}
    request_url = f"{baseurl}/{endpoint}?query=({query})&limit={limit}"
    
    # Make a GET request
    request = requests.get(request_url, headers=headers, params=params)
   
    if request.status_code != 200:
        raise Exception(f"Request failed for {request_url}. {request.text}\n")
    else:
        return request

# Start progress counter
start_date_time = datetime.now()
start = time.time()
num_records = 0

# Start recall stat counters
has_available_items = 0
no_available_items = 0

recalls_to_move = []

# Get all open recalls

get_recalls = make_get_request_w_query_and_limit(
    "circulation/requests", 
    "requestType==\"Recall\" AND status==\"Open - Not yet filled\"", 
    500)

recalls = get_recalls.json()["requests"]

for recall in recalls:
    linked_instance = recall["item"]["instanceId"]

    get_available_items = make_get_request_w_query_and_limit(
        "inventory/items",
        f"instance.id=={linked_instance} AND status.name==\"Available\"",
        100
    )

    items = get_available_items.json()["items"]
    if items:
        recall_id = recall["id"]
        recall_url = auth.uiUrl + f"/requests/view/{recall_id}"
        recalls_to_move.append(recall_url)
        has_available_items +=1
        
    else:
        no_available_items +=1

    # Track progress
    num_records += 1
    if num_records % 10 == 0:
        print("{} recs/s\t{}".format(
            round(num_records/(time.time() - start)),
            num_records), flush=True)

print(
    f"Number of recalls with available items: {has_available_items}"
)
print(
    f"Number of recalls with no available items: {no_available_items}"
)

with open("results/recalls_to_move.txt", "w") as f:
    print(f"This search was intitalized on: {start_date_time}", file=f)
    print(f"Number of recalls with available items: {has_available_items}", file=f)
    print(f"Number of recalls with no available items: {no_available_items}", file=f)   
    print(f"\nRecalls that can be moved to available items:", file=f)
    print(*recalls_to_move, sep = "\n", file=f)