

from pymarc import MARCReader, Record, Field
import sys
import time

inputfile = sys.argv[1]
num_records = 0
start = time.time()

recs = {}

with open(inputfile, 'rb') as sourcefile:
    reader = MARCReader(sourcefile)
    for record in reader:
        rec = []
        rec_data = []
        if record['945'] is not None:
            rec = record.get_fields('945''a')
            for field in rec:
                if 'Chalmers' in field:
                    print('yes!')
                    metadata.append(record['907''a'].data)    
                    print(record)
            
# Display progress
        num_records += 1
        if num_records % 1000 == 0:
            print("{} recs/s\t{}".format(
                round(num_records/(time.time() - start)),
                num_records), flush=True)