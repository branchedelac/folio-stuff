import json
import argparse
import csv
import re
import requests
from gooey import Gooey, GooeyParser
import authqx


@Gooey(program_name='Find json records containing a specified value',
header_bg_color='#FFFFFF',
body_bg_color='#FFFFFF',
footer_bg_color='#FFFFFF',
image_dir='./local_data/',
)

def user_input():
	parser = GooeyParser(description="Specify the file you want to search and the value you're lookign for.")
	parser.add_argument("list", 
						help="A two column csv with old and new instances", 
						widget='FileChooser')
	parser.add_argument("backup", 
						help="Where do you want to save the backed up holdings?",
						widget='FileChooser'),
	parser.add_argument("check", 
						help="Do you want to move the holdings between these instances?")
	args = parser.parse_args()
	args = vars(args)
	return args

# A function for extracting the instance ID from an Inventory URL
def id_from_url(url):
	url_wo_base = re.sub(".*inventory\/view\/", "", url)
	clean_id = re.sub("\?.*", "", url_wo_base)
	return clean_id

# A function for constructing a GET request 
def construct_get_query(endpoint, field, value):
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

# Open a csv with headers and two columns containing:
# old_instance, new_instance
# UUID of the old instance, UUID of the new instance
input = user_input()
infile = input["list"]

# Make sure the person running the script knows what they're doing
if "I do" in input["check"]:
	print(f"Starting to work with {input['list']}...")

# Create an empty list to store the UUIDs of old instances
	old_instances = []
	backup_holdings = []
# Create an empty dictionary to store UUIDs holdings (key) and new instance ids (value)
	new_instances_and_holdings = {}

	# Read csv file into list of list
	with open(infile, "r") as a:	
		reader = csv.reader(a)
		dupe_instances = list(reader)

		for row in dupe_instances[1:]:
			# Work with the old instance: extract and save the id, get the associated holdings
			old_inst = row[0]
			old_inst_id = id_from_url(old_inst)
			old_instances.append(old_inst_id)

			get_associated_holdings = construct_get_query("holdings-storage/holdings", "instanceId", old_inst_id)
			associated_holdings = get_associated_holdings['holdingsRecords']

			# Work with the new instance: extract the UUID, and ad it to dictionary new_instances_and_holdings where associated_holdings_id = value and new_inst_id = key 
			new_inst = row[1]
			new_inst_id = id_from_url(new_inst)

			for holding in associated_holdings:
				# Back up the holding!
				backup_holdings.append(holding)
				holdings_id = holding['id']
				print(f"\nMove holding {holdings_id} from instance {old_inst_id} to {new_inst_id}!")
				new_instances_and_holdings[holdings_id] = [old_inst_id, new_inst_id]
				
				# Change the instanceId value from the current UUID to new_inst_id
				holding['instanceId'] = new_inst_id
				print(f"\n This is what the holding looks like with the new instance ID:\n {holding}\n\n---\n")

	# Print some results
	print("Here's a map of holdings and their old/new instances:\n", new_instances_and_holdings)

	backup_holdings = json.dumps(backup_holdings, ensure_ascii=False)
	print(backup_holdings, file=open(input['backup'], "a"))

else:
	print("Ok! No holdings have been moved.")


#___Move holdings to new instance___
# For each row in csv
#   Add old_inst_id (key) and new_inst_id to dictionary old_and_new_instance_ids (value)
#   From FOLIO, GET all holdings where "instanceId" = old_inst_id and add them to a list
#   For each holding
#       Replace the value in "instanceId" (currently old_inst) to new_inst_id
#       PUT the updated holdings record to FOLIO

#___Delete obsolete records___
# For each row in csv
#   From FOLIO, GET all types of SRS records (all of them!) where "instanceId" = old_inst_id
#   Create a minimal MARC record with DELETE flag (and write to file that we'll send to EDS)
#   From FOLIO, DELETE the SRS records
#   From FOLIO, DELETE the instance old_inst_id


#_____________
# (a) Get a list of all holdings records connected to the old (Enigma) instance
# Query {{baseUrl}}/holdings-storage/holdings?query=(instanceId=="Instance_ID") 
# Input: Current Instance ID
# (a) For each Holdings record, change the Instance ID property to the Libris equivalent in FOLIO
# Input: Current Instance ID, New Instance ID
# (a) Create a MARC record with a delete flag and send it to EDS.
# (a) Delete the SRS record connected to the Enigma Instance
# (a) Delete the Enigma Instance
#_____________