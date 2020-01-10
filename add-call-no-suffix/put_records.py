import sys
import time
import requests
import json

#API Request details 
#TODO: figure out how to not have authentication details in code
headers = {
	'x-okapi-tenant': 'tenant',
	'x-okapi-token': 'token',
	'Content-Type': 'application/json'
}
params = {
	'format': 'json'
}

baseurl = baseurl

#Assign arguments to variables
records_in = sys.argv[1]

#Initiate counters to keep track of progress
num_records = 0
start = time.time()

with open(records_in, 'r') as a:	
	recs_to_put = json.load(a)

for rec in recs_to_put[1:3]:
	hldid = rec['id']
	request_url = f'{baseurl}/holdings-storage/holdings/{hldid}'
	body = json.dumps(rec, ensure_ascii=False)
	request = requests.put(request_url, data=body, headers=headers, params=params)
	
	status = request.status_code

	if request.status_code != 204:
		print(f'Something went wrong with {hldid}! Status code: {status}')
	
	#Track progress and speed going through the items on the list
	num_records += 1
	if num_records % 50 == 0:
		print("{} recs/s\t{}".format(
			round(num_records/(time.time() - start)),
			num_records), flush=True)

	print(request_url)
	print(body)