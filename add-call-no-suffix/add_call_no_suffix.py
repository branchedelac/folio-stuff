import sys
import json
import csv

print('Let\'s start!')

#items_export = sys.argv[1]
#hld_export = sys.argv[2]
#items_suffix_map = sys.argv[3]
#hld_suffix_map = sys.argv[4]
#hld_suffix_added = sys.argv[5]

with open('test_holdings.json', 'r') as a:
	hld_wo_suffix = json.load(a)

	for record in hld_wo_suffix:
		print('Before:\n', record, '\n')
		print()
		with open('test_hldid_suffix_map.csv', 'r') as b:
			hldid_suffix_map = csv.DictReader(b)
			for row in hldid_suffix_map:
				if record['id'] in row['hld_id']:
				#print('ID: ' + record['id'] + '\tSuffix: ' + row['suffix'])
					record['callNumberSuffix'] = row['suffix']
		print('After:\n', record)
		if record['callNumberSuffix'] in '':
			print('Couldn\'t find ID in map!')
		print('\n...\n')




