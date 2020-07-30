#WIP

# Read file, create dictionary with FOLIO UUID (999 $i) as key, and an list of identifiers as value

import json
import argparse
import time
import requests
from requests.exceptions import HTTPError

parser = argparse.ArgumentParser()
parser.add_argument("infile", help="A file to analyze", type=str)
parser.add_argument("matchout", help="Save a list of 'match objects' (FOLIO instance id, ISBN, ISSN) here", type=str)
args = parser.parse_args()

# Define a function which gets all the *values* of a certain field and subfield combination (eg all 020 $a) and stores them in a list

def get_subfield_values(record, field_code, subfield_code):
    all_subfield_values = []
    marc_record = record["fields"]
    for field in marc_record:
        if field_code in field:
            try:
                subfields = field[field_code]["subfields"]
                for subfield in subfields: 
                    subfield_value = subfield[subfield_code]
                    all_subfield_values.append(subfield_value)
            except KeyError as k1:
                errors.append(f"Subfield object or subfield code{k1} missing for {record}")
                continue
    return all_subfield_values

def make_get_request(value, field):
    url = f"https://libris.kb.se/find.json?identifiedBy.value={value}&identifiedBy.@type={field}&@type=Instance"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Request failed for {value}. {response.text}\n")
    else:
        return response

def get_libris_matches(json_response):
        xl_ids = []
        for item in parsed_response["items"]:
            xl_id = item["@id"]
            xl_ids.append(xl_id)
            return xl_ids

# Define a class for a "match object", which contains FOLIO instance UUID, ISBN and ISSN (and could be extended with title, author, normalized versions of various values etc)
# TODO Add other matchable data like title 

class MatchObject:
      def __init__(self, record):
          self.folio_inst_id = get_subfield_values(record, "999", "i")
          self.isbn = get_subfield_values(record, "020", "a")
          self.issn = get_subfield_values(record, "022", "a")
          self.matched_xl_id = ""

# Set up some variables to store data in
printable_match_objects = []
errors = []
no_isn = []
has_isbn = []
has_issn = []
has_both = []

#Initiate counters to keep track of progress
num_records = 0
start = time.time()


# Start working with the data

with open(args.infile) as f1, open(args.matchout, "a") as f2:
    local_records = json.load(f1)

    for record in local_records[:10]:
        object = MatchObject(record)
        printable_match_objects.append(vars(object))
        
        # TODO Try to match on title etc
        if (not object.isbn) and (not object.issn):
            no_isn.append(object)
        
        elif object.isbn and not object.issn:
            has_isbn.append(object)
            for isbn in object.isbn:
                libris_response = make_get_request(isbn, "ISBN")
                time.sleep(0.01)
                
                parsed_response = libris_response.json()
                if parsed_response["totalItems"] > 0:
                    libris_matches = get_libris_matches(parsed_response)
                    if len(libris_matches) == 1:
                        object.matched_xl_id = libris_matches[0]
                        # print(f"{isbn} matches {object.matched_xl_id}")
                else:
                    print(f"No match for {isbn}!")


        elif object.issn and not object.isbn:
            has_issn.append(object)

            for issn in object.issn:
                libris_response = make_get_request(issn, "ISSN")
                time.sleep(0.01)
                
                parsed_response = libris_response.json()
                
                if parsed_response["totalItems"] > 0:
                    libris_matches = get_libris_matches(parsed_response)
                    if len(libris_matches) == 1:
                        object.matched_xl_id = libris_matches[0]
                        # print(f"{isbn} matches {object.matched_xl_id}")
                else:
                    print(f"No match for {isbn}!")

        else:
        # This is an edge case case, if they have both ISSN and ISBN, let's just print it so a cataloguer can have a look
            has_both.append(vars(object))
        
        print(vars(object))
                

        #Track progress and speed going through the items on the list
        num_records += 1
        if num_records % 2000 == 0:
            print("{} recs/s\t{}".format(
                round(num_records/(time.time() - start)),
                num_records), flush=True)

# Print some results to a file
with open(args.matchout, "a") as f2: 
    print("First some numbers:", file=f2)
    print("Records with no ISN:", len(no_isn), file=f2)
    print("Records with ISBN:", len(has_isbn), file=f2)
    print("Records with ISSN:", len(has_issn), file=f2)
    print(f"Records with ISBN and ISSN: {len(has_both)}\n", *has_both, sep="\n",file=f2)
    print("Numer of data errors:", len(errors), file=f2)
    print("\nErrors:\n", *errors, sep="\n", file=f2)