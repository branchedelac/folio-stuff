import sys
import time
import requests
import json

#Assign arguments (should be a json file of FOLIO holdings records) to variable
local = sys.argv[1]
records_in = sys.argv[2]
list_out = sys.argv[3]


#Get request headers and base URL from local file 
with open(local, 'r') as auth:	
	auth_data = json.load(auth)

headers = {
	'x-okapi-tenant': auth_data['okapi-tenant'],
	'x-okapi-token': auth_data['okapi-token'],
	'Content-Type': 'application/json; charset=utf-8'
}
params = {
	'format': 'json'
}
baseurl = auth_data['okapi-url']


#Initiate counters to keep track of progress
num_records = 0
start = time.time()

#Initiate list of clickable URLs to updated holdings
click_urls = []

with open(records_in, 'r') as a:	
	recs_to_put = json.load(a)

for rec in recs_to_put[20:]:
	#Assign variables to create the request URL and request body
	hldid = rec['id']
	request_url = f'{baseurl}/holdings-storage/holdings/{hldid}'
	body = json.dumps(rec, ensure_ascii=False)
	#Make a PUT request to the holdings storage API, with the record in the request body
	request = requests.put(request_url, data=body.encode('utf-8'), headers=headers, params=params)

	#Check that the status code is 204 (success) - if it isn't, print info about this!
	status = request.status_code

	if request.status_code == 204:
		#Add a clickable URL to a list of INSTANCES whose holdings have been added 
		instance_id = rec['instanceId']
		uiurl = auth_data['ui-url']
		click_url = f'{uiurl}/inventory/view/{instance_id}'
		click_urls.append(click_url)

	elif request.status_code != 204:
		print(f'Something went wrong with {hldid}! Status code: {status}')
	
	#Track progress and speed going through the items on the list
	num_records += 1
	if num_records % 50 == 0:
		print("{} recs/s\t{}".format(
			round(num_records/(time.time() - start)),
			num_records), flush=True)

	#Give FOLIO some rest before sending the next request
	time.sleep(0.01)

print(click_urls, file=open(list_out, "a"))
