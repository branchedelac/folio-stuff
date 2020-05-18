import sys
import time
import requests
import json
import auth

# Initiate counter to keep record (haha) of how many requests we've sent.
iteration = 0

# Initiate a list that we will put the returned json data in
result = []

# We'll set offset to 0 from the start, then increment by limit after each iteration
offset = 0

# Set a variable someleft to True. This will let us know when we've itreated through all existing records.
someleft = True

# Create the different parts of the request 
baseurl = auth.okapiUrl
module = "/source-storage/sourceRecords"
limit = int(sys.argv[1])

headers = {
	'x-okapi-tenant': auth.xOkapiTenant,
	'x-okapi-token': auth.xOkapiToken
}

params = {
	'format': 'json'
}

# Name the file where you want to place the output
outputfile = sys.argv[2]

# Keep looping through the code below as long as someleft == True 
while someleft:
	
	iteration += 1

	print(f"Working on request number {iteration}!")
	# Build a request URL and send the GET request to the item storage API
	request_url = f'{baseurl}{module}?limit={limit}&offset={offset}'

	print(request_url, "\n")

 	#Send the GET request to the item storage API
	request = requests.get(request_url, headers=headers, params=params)

 	# Check that the response is 200 (success)
	if request.status_code != 200:
		print(request.status_code)
		break 
	else:
		response = request.json()
		# Check that we are still getting any records back...
		if len(response['sourceRecords']) != 0:
			result.extend(response['sourceRecords'])
			# Increment the offset by the limit value
			offset += limit
			# Give FOLIO some rest before making the next request
			time.sleep(0.01)
		else:
			# When response['items'] is empty, we've retreived all existing records. Set someleft to False, to get out of the loop.
			someleft = False

# Ok. We have our records! Now transform the list into json
resultjson = json.dumps(result, ensure_ascii=False)

# Print the result to a file
print(resultjson, file=open(outputfile, "a"))