import sys
import time
import requests
import json
import auth

# Define some request details 
headers = {
	'x-okapi-tenant': auth.xOkapiTenant,
	'x-okapi-token': auth.xOkapiToken
}
params = {
	'format': 'json'
}

baseurl = auth.okapiUrl
query = '/item-storage/items?query=(effectiveLocationId=="5fb1c433-7b29-4226-8054-f8d491cf8426")&limit=1000&offset='
# We'll set offset to 0 from the start, then increment after each iteration
offset = 0

# Initiate a list that we will put the returned json data in
result = []

# Set a variable someleft to True
someleft = True

# Keep looping through the code below as long as someleft == True 
while someleft:
	print("Working on it!")
	# Build a request URL and send the GET request to the item storage API
	request_url = f'{baseurl}{query}{offset}'
	print(request_url)
	request = requests.get(request_url, headers=headers, params=params)
	# Check that the response is 200 (success)
	if request.status_code != 200:
		print(request.status_code)
	else:
		response = request.json()
		# Check that we are still getting any records back...
		if len(response['items']) != 0:
			result.extend(response['items'])
			# Increment the offset by the limit value
			offset += 1000
			# Give FOLIO some rest before making the next request
			time.sleep(0.01)
		else:
			# When response['items'] is empty, we've retreived all existing records. Set someleft to False, to get out of the loop.
			someleft = False

# Ok. We have our records! Now transform the list into json
resultjson = json.dumps(result, ensure_ascii=False)

# Print the result to a file
print(resultjson, file=open("items-patricia.json", "a"))