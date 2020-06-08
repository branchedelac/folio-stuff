import json
import argparse
import csv
import re
import requests
from gooey import Gooey, GooeyParser
import authqx


@Gooey(program_name='Move FOLIO holdings between instances',
header_bg_color='#FFFFFF',
body_bg_color='#FFFFFF',
footer_bg_color='#FFFFFF',
image_dir='./local_data/',
)

def user_input():
	parser = GooeyParser(description="Please fill in all the fields below.")
	parser.add_argument("list_of_records", 
						help="A comma separated list, with headers and two column, of Inventory URLs to the instances you want to move holdings FROM and the instances you want to move holdigns TO.", 
						widget='FileChooser')
	parser.add_argument("save_backup", 
						help="Where do you want to save the backed up holdings?",
						widget='FileChooser'),
	parser.add_argument("save_ids", 
						help="Where do you want to save the list of obsolete instances to delete?",
						widget='FileChooser'),
	parser.add_argument("check", 
						help="Do you really want to move the holdings between the instances specified in the list of records?")
	args = parser.parse_args()
	args = vars(args)
	return args

# A function for extracting the instance ID from an Inventory URL
def id_from_url(url):
	url_wo_base = re.sub(".*inventory\/view\/", "", url)
	clean_id = re.sub("\?.*", "", url_wo_base)
	return clean_id

# A function for making a GET request with a query
def make_get_request_w_query(endpoint, field, value):
	baseurl = authqx.okapiUrl

	headers = {'x-okapi-tenant': authqx.xOkapiTenant, 'x-okapi-token': authqx.xOkapiToken}
	params = {'format': 'json'}
	request_url = f"{baseurl}/{endpoint}?query=({field}={value})"
	
	print(f"\nFetching records: {request_url}")

	# Make a GET request
	request = requests.get(request_url, headers=headers, params=params)
	# If the status code is 200, parse the response as json
	if request.status_code == 200:
		response = request.json()
		return response
	else:
		print(f"Something went wrong with {request_url}! Status code: {request.status_code}.")

# A function for making a PUT request with a query
def make_put_request(endpoint, uuid, body):
	baseurl = authqx.okapiUrl

	headers = {'x-okapi-tenant': authqx.xOkapiTenant, 
	'x-okapi-token': authqx.xOkapiToken, 	
	'Content-Type': 'application/json; charset=utf-8'
}
	params = {'format': 'json'}
	request_url = f"{baseurl}/{endpoint}/{uuid}"
	
	print(f"\nPutting record: {request_url}")

	request = requests.put(request_url, data=body.encode('utf-8'), headers=headers, params=params)

	# Check that the status code is 204 (success) - if it isn't, print info about this!
	status = request.status_code
	if request.status_code != 204:
		print(f"\nSomething went wrong with {uuid}! Status code: {status}")
	else:
		return status

# Open a csv with headers and two columns containing:
# old_instance, new_instance
# UUID of the old instance, UUID of the new instance
input = user_input()
infile = input["list_of_records"]

# Make sure the person running the script knows what they're doing
if "I do" in input["check"]:
	print(f"...\nStarting to work with {input['list_of_records']}...")

# Create an empty list to store the UUIDs of old instances
	old_instances = []
	backup_holdings = []
	qnty_replaced = 0
	qnty_reassociated = 0
# Create an empty dictionary to store UUIDs holdings (key) and new instance ids (value)
	new_instances_and_holdings = {}

	# Read csv file into list of list
	with open(infile, "r") as a:	
		reader = csv.reader(a)
		dupe_instances = list(reader)

		for row in dupe_instances[1:]:
			# Work with the old instance: extract and save the id, 
			old_inst = row[0]
			old_inst_id = id_from_url(old_inst)

			# Get all holdings for this instanceId
			get_associated_holdings = make_get_request_w_query("holdings-storage/holdings", "instanceId", old_inst_id)
			holdings = get_associated_holdings['holdingsRecords']
			
			if len(holdings) > 0:
				# Work with the new instance
				new_inst = row[1]
				new_inst_id = id_from_url(new_inst)

				for holding in holdings:
					# Back up the holding!
					backup_holdings.append(holding)
					
					holdings_id = holding['id']

					print(f"\nMove holding {holdings_id} from instance {old_inst_id} to instance {new_inst_id}!")
					new_instances_and_holdings[holdings_id] = [old_inst_id, new_inst_id]
					
					# Change the instanceId value from the current UUID to new_inst_id
					holding['instanceId'] = new_inst_id
					reassociated_holding = json.dumps(holding, ensure_ascii=False)

					# PUT the reassociated holding to FOLIO
					success = make_put_request("holdings-storage/holdings", holdings_id, reassociated_holding)
					if success:
						qnty_reassociated += 1
						print(f"\nHolding {holdings_id} successfully updated in FOLIO!")

						# Append now obsolete inst_id to list, for future use
						if old_inst_id not in old_instances:
							old_instances.append(old_inst_id)
							qnty_replaced += 1
			else:
				print(f"\nNo holdings found for {old_inst_id}!")

	# Print some results
	backup_holdings = json.dumps(backup_holdings, ensure_ascii=False)
	print(f"A map of holdings and their old + new instances:\n {new_instances_and_holdings} \n\nBacked up holdings:\n {backup_holdings}", file=open(input['save_backup'], "a"))
	print(old_instances, file=open(input['save_ids'], "a"))

	print(f"\n---\n\n{qnty_replaced} instances have been replaced, and {qnty_reassociated} holdings successfully reassociated. \n\n A map of holdings and old + new instance UUIDs, as well as a list of UUIDs for now obsolete instances, have been saved to the desired location.")

else:
	print("Ok! No holdings have been moved.")