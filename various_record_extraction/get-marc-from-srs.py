import sys
import json

records_in = sys.argv[1]
records_out = sys.argv[2]

parsed_recs = []

with open(records_in, 'r') as a:
	srs_recs = json.load(a)
	for rec in srs_recs:
		parsed_recs.append(rec['parsedRecord']['content'])

parsed_json = json.dumps(parsed_recs, ensure_ascii=False)

print(parsed_json, file=open(records_out, "a"))
