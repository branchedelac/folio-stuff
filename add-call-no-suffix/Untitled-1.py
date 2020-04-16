

from pymarc import MARCReader
import sys
import time

inputfile = sys.argv[1]
num_records = 0
start = time.time()

recs = {}

with open(inputfile, 'rb') as sourcefile:
    reader = MARCReader(sourcefile)
    for record in reader:
    metadata = []
        if record['945'] is not None:
            if 'maris' in record['945']:
            metadata.append(record['945''a'].data)    
print(record)
            
# Display progress
        num_records += 1
        if num_records % 10000 == 0:
            print("{} recs/s\t{}".format(
                round(num_records/(time.time() - start)),
                num_records), flush=True)