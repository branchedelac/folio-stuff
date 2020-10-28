import sys
import time
import requests
import json
import csv

# TODO: figure out how to not have authentication details in code
# Utilize Inventory cross record search, e.g. holdings-storage/holdigns?query=item.barcode

headers = {
	'x-okapi-tenant': 'tenant',
	'x-okapi-token': 'token'
}
params = {
	'format': 'json'
}

baseurl = 'baseurl'

#Assign arguments to variables
map_in = sys.argv[1]
old_hlds_backup = sys.argv[2]
updated_records_out = sys.argv[3]

#Initiate dcitionary where we will store the barcode ID (extracted from the csv file) as key and the holdings ID (extracted from the item record) as value
barcode_hld_map = {}
#Initiate dcitionary where we will store the holdings ID (extracted from the item record) as key and the call number suffix (extracted from the csv file) as value
hld_suff_map = {}

#Initiate counters to keep track of progress
num_records = 0
start = time.time()

#Open the csv file containing identifiers of the records you want to edit, and read it into a dictionary
with open(map_in, 'r') as a:	
	sierra_items = csv.DictReader(a)
	
	#Iterating over dictionary items, add the barcode value to the request URL
	for row in sierra_items:
		if row['barcode'] not in '':
			barcode = row['barcode']
			request_url = f'{baseurl}/inventory/items?query=barcode=={barcode}'
			#Make a GET request to the item API
			request = requests.get(request_url, headers=headers, params=params)

			#Check that the response is 200
			if request.status_code == 200:
				#Work with the response
				response = request.json()
				item_rec = response['items']

				#Verify that only one record was returned
				if len(item_rec) == 1:
					item_rec = item_rec[0]
					#Add holdingsRecordId to barcode_hld_map
					hld_id = item_rec['holdingsRecordId']
					hld_suff_map[hld_id] = row['callno_suffix']
					barcode_hld_map[row['barcode']] = hld_id 
				#If more or less than one record was returned, print the barcode
				elif len(item_rec) > 1:
					print(f'Too many matches for {barcode}!')
			else:
				print('No match for barcode', barcode)

			#Give FOLIO some rest before sending the next request
			time.sleep(0.01)
		
		else:
			print('No barcode for', row['sierra_id'], '. Fix this one manually!')

		#Track progress and speed going through the items on the list
		num_records += 1
		if num_records % 50 == 0:
			print("{} recs/s\t{}".format(
				round(num_records/(time.time() - start)),
				num_records), flush=True)

#Here's a map of barcodes and holdings IDs, which
print('\nHere is our barcode - holdings id map! It contains', len(barcode_hld_map), 'pairs. \n', barcode_hld_map)

#Ok, we have our map of holdings IDs and call no suffixes and are DONE with the csv table!
#Print the map to have a look!
print('\nHere is our holdings ID - call number suffix map! It contains', len(hld_suff_map), 'pairs. \n', hld_suff_map)



#Now, let's fetch the holdings that we want to edit! We have the IDs in hld_suff_map.

print('\nLet\'s srtart fetching holdings records!')
#Initiate list to store fetched holdings records
hld_recs =  []

#Iterating over dictionary items, add the key to the request URL
for hld in hld_suff_map:
	id = hld
	request_url = f'https://okapi-fse-eu-central-1.folio.ebsco.com/holdings-storage/holdings/{id}'

	#Make a GET request to the holdings storage API
	request = requests.get(request_url, headers=headers, params=params)

	#Check that the response is 200
	if request.status_code == 200:
		#Work with the response
		response = request.json()
		hld_recs.append(response)
	else:
		print('No match for holding id', id)

	#Give FOLIO some rest before sending the next request
	time.sleep(0.01)

#Print a backup file with all the extracted holdings
old_holdings = json.dumps(hld_recs, ensure_ascii=False)
print(old_holdings, file=open(old_hlds_backup, "a"))

#Wow! Now it's time to add the call number suffixes in the map to the right holding record.
print('\nLet\'s srtart adding call number suffixes to holdings records!\n')

#Loop through holdings IDs in the holdings - suffix map, comparing them to the ID of each of the holdings ín the hld_recs list.
for hld in hld_suff_map:
	for rec in hld_recs:
		#If the IDs match, check if the holdings record already has a call number suffix field with a value. If it doesn't, assign a key value pair where the value is the corresponding value from the hld_suff_map dictionary.
		if hld in rec['id']:
			#If the key does not exist in the dicitonary (the record does not have the field), a new key-value pair will be added.
			if 'callNumberSuffix' not in rec:
				rec['callNumberSuffix'] = hld_suff_map[hld]
				print('Added a brand new field + value to holding', hld)
			#If the key already exists in the dictionary and the value is '' (the record has the field but it's empty), the old value will be replaced.
			elif rec['callNumberSuffix'] in '':
				rec['callNumberSuffix'] = hld_suff_map[hld]
			#If the key already exists and the value is not '', some awesome librarian has probably added it manually. Print a happy message!
			else:
				print('Holding', hld,'already has a call number suffix. Awesome!')

#Convert the json dictionary to a string
updated_holdings = json.dumps(hld_recs, ensure_ascii=False)

#Print the records to a file
print(updated_holdings, file=open(updated_records_out, "a"))