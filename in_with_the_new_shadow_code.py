# TODO Införliva feedback från Theodor:
# Använd Python truth istället för None DONE
# Förfina PUT-request DONE
# Fixa ödesdiger bugg DONE
# Deindentera huvuddelen med något som avslutar skriptet DONE
# Objektorientera mera
# Använd exceptions (läs på, testa, fundera på var de kan vara till användning, implementera)
# Lägga instansidn i tuple (de ska vara två!) istället för lista i dict DONE
# Fixa så att moduler inte är rödprickade i VS Code DONE
# Utforska hur man kan konstruera urlar med requests 
  
# TODO Införliva feedback från Siska: 
# Vad händer om det finns dependencies till t.ex. lån, ordrar, osv (minns att vi diskuterat detta med Charlotte - borde testa). Lån verkar klara sig, däremot är det knepigt med öppna ordrar.

# TODO Var lagra tenant-specifika värden (t.ex. okapi-url, token)? 
# Fundera på Utforska t.ex .env och configparser


import json
import argparse
import csv
import re
import requests
import time
import traceback
from gooey import Gooey, GooeyParser
from datetime import timedelta
# Var är det bäst att lagra alla sina tenant-specifika tokens etc?
import authqx as auth

# Add some cool design to the gooey UI
@Gooey(program_name='Move FOLIO holdings between instances',
header_bg_color='#FFFFFF',
body_bg_color='#FFFFFF',
footer_bg_color='#FFFFFF',
image_dir='./local_data/',
)

# I'm not sure why I made this a function rather than part of the 'main' script
def user_input():
    parser = GooeyParser(description="Please fill in all the fields below.")
    parser.add_argument("list_of_records", 
                        help="A two column csv containing Inventory URLs for to the instances you want to move holdings FROM and TO. See format below: \n\nfrom_instance,to_instance\nuuid1a,uuid1b\nuuid2a,uuid2b", 
                        widget='FileChooser')
    parser.add_argument("backup", 
                        help="Where do you want to save the backed up holdings?",
                        widget='FileChooser'),
    parser.add_argument("report", 
                        help="Where do you want to save the report (errors, etc)?",
                        widget='FileChooser'),
    parser.add_argument("disconnected_instances", 
                        help="Where do you want to save the list of obsolete instances to delete?",
                        widget='FileChooser'),
    parser.add_argument("check", 
                        help="Do you really want to move the holdings between the instances specified in the list of records?")
    args = parser.parse_args()
    args = vars(args)
    return args

# Define a function that extractis the instance ID from an Inventory URL
def id_from_url(url):

    url_wo_base = re.sub(".*inventory\/view\/", "", url)
    clean_id = re.sub("\?.*", "", url_wo_base)

    # Verify that what we have is a valid UUID (pattern from https://dev.folio.org/guides/uuids/)
    uuid_pattern = re.compile("^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[1-5][a-fA-F0-9]{3}-[89abAB][a-fA-F0-9]{3}-[a-fA-F0-9]{12}$")
    if uuid_pattern.match(clean_id):
        return clean_id
    else:
        raise ValueError(f"Unable to extract instance UUID from {url}")


# Define a function that sets base url and headers for API requests
def set_local_variables():
    local_variables = {
        'baseurl' : auth.okapiUrl,
        'headers' : {'x-okapi-tenant': auth.xOkapiTenant, 'x-okapi-token': auth.xOkapiToken}
    }

    return local_variables


# Define a function that makes a GET request with a CQL query
# TODO Explore putting parametres like query, limit, offset in the params dict
def make_get_request_w_query(endpoint, field, value):
    local_variables = set_local_variables()

    baseurl = local_variables['baseurl']
    headers = local_variables['headers']
    params = {'format': 'json'}
    request_url = f"{baseurl}/{endpoint}?query=({field}={value})"
    
    #print(f"\nFetching holdings for {request_url}")

    # Make a GET request
    request = requests.get(request_url, headers=headers, params=params)
   
    if request.status_code != 200:
        raise Exception(f"Request failed for {request_url}. {request.text}\n")
    else:
        return request

# Define a function that makes a PUT request with a json object as the body
def make_put_request(endpoint, uuid, body):
    local_variables = set_local_variables()

    baseurl = local_variables['baseurl']
    headers = local_variables['headers']

    headers['Content-Type'] = 'application/json; charset=utf-8'

    params = {'format': 'json'}
    request_url = f"{baseurl}/{endpoint}/{uuid}"
    
    #print(f"\nPutting updated holding to {request_url}")

    request = requests.put(request_url, json=body, headers=headers, params=params)

    # Check that the status code is 204 (success) - if it isn't, print info about this!
    if request.status_code != 204:
        raise Exception(f"Request failed for {request_url}. {request.text}\n")
    else:
        return request
        
# Open a csv with a header row and two columns containing:
# from_instance, to_instance
# UUID of the old instance, UUID of the new instance
input = user_input()
infile = input["list_of_records"]

# Make sure the person running the script knows what they're doing
if "I do" != input["check"]:
    exit("Looks like you didn't really want to move any holdings between instances. That's ok! No holdings have been moved.")

print(f"...\nStarting to work with {input['list_of_records']}... in {auth.okapiUrl}\n")

# Create empty lists where we'll store obsolete instance UUIDs and backed up holdings
from_instances = []
backup_holdings = []
failed_rows_report = []
error_report = []
# Create an empty dictionary to store holdings UUIDs(key) and old + new instance UUDS (value)
relinked_instances_and_holdings = {}

# Initiate counters to keep track of how many instances we've moved holdings from, and how many holdings we've moved
qnty_replaced = 0
qnty_reassociated = 0
#Initiate counters to keep track of progress
num_records = 0
start = time.time()


# Read csv file into a dict
try:
    with open(infile, "r") as a:	
        dupe_instances = csv.DictReader(a)

        # Iterate through the dict of IDs
        for row in dupe_instances:
            try:
                # Extract and save the UUID of the old instance (column "from_instance")
                from_inst = row['from_instance']
                from_inst_id = id_from_url(from_inst)

                # Extract and save the UUID of the new instance
                to_inst = row['to_instance']
                to_inst_id = id_from_url(to_inst)

            except ValueError as v1:
                failed_rows_report.append(row)
                error_report.append(v1)
                print(v1, "Skip to next row.")
                continue

            # If we fail to extract a UUID, skipt to the end of this for loop. Otherwise... 
            try: 
                # Get all holdings for this instanceId
                get_associated_holdings = make_get_request_w_query("holdings-storage/holdings", "instanceId", from_inst_id)
                parsed_holdings = get_associated_holdings.json()
                # TODO Handle exception if the response is empty (ie not [] holdings, but request failed)
                holdings = parsed_holdings['holdingsRecords']
                # Make sure FOLIO gets some rest before the next API request
                time.sleep(0.01)
                
                if not any(holdings):
                    raise ValueError(f"No holdings found for {from_inst_id}")
            
            except ValueError as v2:
                print(f"{v2}. Skip to next row.")
                failed_rows_report.append(row)
                error_report.append(v2)
                continue

            except Exception as e1:
                print(f"{e1}. Skip to next row.")
                error_report.append(e1)
                failed_rows_report.append(row)
                continue

            # If any holdings were returned, we want to move them to the new instance (index 1)
            try:
                for holding in holdings:
                    # Back up the holding json object!
                    backup_holdings.append(holding)
                    # Add the holdings ID (key), and a list of from_inst_id and to_inst_id (value), to dictionary relinked_instances_and_holdings
                    holdings_id = holding['id']
                    relinked_instances_and_holdings[holdings_id] = (from_inst_id, to_inst_id)
                    
                    # Change the instanceId value from the current UUID to to_inst_id
                    holding['instanceId'] = to_inst_id
                    reassociated_holding = holding
                    
                    # PUT the reassociated holding to FOLIO
                    success = make_put_request("holdings-storage/holdings", holdings_id, reassociated_holding)
                    if success:
                        print(f"\nHoldings successfully moved from {from_inst_id} to {to_inst_id}\n")
                        qnty_reassociated += 1
                        # Append now obsolete from_inst_id to list from_instances, for future use
                        if from_inst_id not in from_instances:
                            from_instances.append(from_inst_id)
                            qnty_replaced += 1

            except Exception as e2:
                failed_rows_report.append(row)
                error_report.append(e2)
                print(e2)
                break 
                # Make sure FOLIO gets some rest before the next API request
                time.sleep(0.01)
            # else:
            #     print(f"\nNo holdings found for {from_inst_id}\n")


        #Track progress and speed going through the items on the list
        num_records += 1
        if num_records % 10 == 0:
            print("{} recs/s\t{}".format(
                round(num_records/(time.time() - start)),
                num_records), flush=True)
                
# Print a result summary in the terminal
finally:
    elapsed = (time.time() - start)
    print(f"\n---\n\n{qnty_replaced} instances have been dsiconnected from their previous holdings, and {qnty_reassociated} holdings successfully reassociated.\nDuration of the process: {str(timedelta(seconds=elapsed))}")
    if qnty_replaced > 0:
        # Print some results to two files
        backup_holdings = json.dumps(backup_holdings, ensure_ascii=False)
        print(f"A map of holdings and their old + new instances:\n {relinked_instances_and_holdings} \n\nBacked up holdings:\n{backup_holdings}", file=open(input['backup'], "a"))
        print(from_instances, file=open(input['disconnected_instances'], "a"))
        print("\n A map of holdings and old + new instance UUIDs, as well as a list of UUIDs for now obsolete instances, have been saved to the desired location.")

    print("Errors:\n", *error_report, sep = "\n", file=open(input['report'], "a"))
    print("\n...\n", "Failed rows:\n", failed_rows_report, file=open(input['report'], "a"))
