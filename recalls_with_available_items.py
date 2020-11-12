# Listan Recalls_to_move.txt som tas ut med scriptet recalls_with_available_items.py

# Det vore superbra att få med lite fler element för att lättare arbeta med listan och flytta den person som stått längst i kö till det/de tillgängliga exemplaren.

# Maries förslag:
# InstansID Titel Request date Requester RequestID

# Vi behöver inte böka med sortering, men OM det skulle vara jätteenkelt så kanske:
# 1. Instans-ID
# 2. Request date
# eller bara Request date



'''
One shortcoming of current requesting functionality in FOLIO, where recall requests are associated with a specific copy directly upon creation, is that a patron may be left queueing for one specific copy even after another copy has become available.
This script identifies open recall requests where the associated instance has at last one available copy. Once these requests have been identified, a can will go into FOLIO and manually move the request to an available item.
'''

import time
from datetime import datetime
import requests

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

# Fetch all open recall requests

get_recalls = make_get_request_w_query_and_limit(
    "circulation/requests", 
    "requestType==\"Recall\" AND status==\"Open - Not yet filled\"", 
    500)

recalls = get_recalls.json()["requests"]

# Loop throgh fetched recall requestes
for recall in recalls:
    request_date = recall["requestDate"]
    linked_instance = recall["item"]["instanceId"]
    title = recall["item"]["title"]

    # Fetch items associated with the instance that are available and loanable
    get_available_items = make_get_request_w_query_and_limit(
        "inventory/items",
        f"instance.id=={linked_instance} AND status.name==\"Available\" AND permanentLoanTypeId==\"11fbed26-571e-40fb-9e26-80605602021d\"",
        100
    )

    # If there are any items available and loanable, add the recall request to list recalls_to_move
    items = get_available_items.json()["items"]

    if items:
        recall_id = recall["id"]
        recall_url = auth.uiUrl + f"/requests/view/{recall_id}"
        requester = recall["requester"]["lastName"]

        recall_info = f"{linked_instance}    {recall_url}    ({request_date} {requester})    {title}"

        recalls_to_move.append(recall_info)
        has_available_items +=1
        
    else:
        no_available_items +=1

    # Track progress
    num_records += 1
    if num_records % 10 == 0:
        print("{} recs/s\t{}".format(
            round(num_records/(time.time() - start)),
            num_records), flush=True)
    
    # Give FOLIO some rest before moving on to the next request
    time.sleep(0.01)

# Wrapping up... print summary to console
print(
    f"Number of recalls with available items: {has_available_items}"
)
print(
    f"Number of recalls with no available items: {no_available_items}"
)

# Print results and list of recalls to move to a file in directory results. If a file by the name already exists, it will be overwritten. 

sorted_recalls_to_move = sorted(recalls_to_move)


with open("results/recalls_to_move.txt", "w") as f:
    print(f"This search was intitalized on: {start_date_time}", file=f)
    print(f"Number of recalls with available items: {has_available_items}", file=f)
    print(f"Number of recalls with no available items: {no_available_items}", file=f)   
    print(f"\nRecalls that can be moved to available items:", file=f)
    print(*sorted_recalls_to_move, sep = "\n", file=f)