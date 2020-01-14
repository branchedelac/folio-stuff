import sys
import json

baseurl = 'baseurl'

#Assign argument (should be a json file of FOLIO holdings records) to variable
records_in = sys.argv[1]

#Initiate counters to keep track of progress

with open(records_in, 'r') as a:	
	recs_to_put = json.load(a)

#Loop through holdings records to create a clickable URL 
for rec in recs_to_put:
	#Assign variables to create the request URL and request body
	instance_id = rec['instanceId']
	request_url = f'{baseurl}/inventory/view/{instance_id}'
	print(request_url)
