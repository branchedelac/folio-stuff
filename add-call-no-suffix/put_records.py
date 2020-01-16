import sys
import time
import requests
import json

#API Request details 
#TODO: figure out how to not have authentication details in code
headers = {
	'x-okapi-tenant': 'tenant',
	'x-okapi-token': 'token',
	'Content-Type': 'application/json; charset=utf-8'
}
params = {
	'format': 'json'
}

baseurl = 'baseurl'

#Assign argument (should be a json file of FOLIO holdings records) to variable
records_in = sys.argv[1]

#Initiate counters to keep track of progress
num_records = 0
start = time.time()

with open(records_in, 'r') as a:	
	recs_to_put = json.load(a)

#Loop through holdings records to create a URL 
for rec in recs_to_put:
	#Assign variables to create the request URL and request body
	hldid = rec['id']
	request_url = f'{baseurl}/holdings-storage/holdings/{hldid}'
	body = json.dumps(rec, ensure_ascii=False)

	#Make a PUT request to the holdings storage API, with the record in the request body
	request = requests.put(request_url, data=body.encode('utf-8'), headers=headers, params=params)
	
	#Check that the status code is 204 (success) - if it isn't, print info about this!
	status = request.status_code
	if request.status_code != 204:
		print(f'Something went wrong with {hldid}! Status code: {status}')
	
	#Track progress and speed going through the items on the list
	num_records += 1
	if num_records % 50 == 0:
		print("{} recs/s\t{}".format(
			round(num_records/(time.time() - start)),
			num_records), flush=True)

	#Give FOLIO some rest before sending the next request
	time.sleep(0.01)

	#print(request_url)
	#print(body)