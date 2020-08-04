# Work in progress 
# NB Current version not tested on full dataset
# TODO Fix bug which adds record to IS[B/S]N_matched AND no_isn_matched AND too_many_matches if the record has several ISNs which meet different matching conditions.

import json
import argparse
import time
import re
import requests
from requests.exceptions import HTTPError

parser = argparse.ArgumentParser()
parser.add_argument("infile", help="A file to analyze", type=str)
parser.add_argument("stats", help="Output statistics and results summary here", type=str)
parser.add_argument("noissn", help="Output a list of objects without ISSN", type=str)
parser.add_argument("isnmatch", help="Output FOLIO instance UUID, ISBN/ISSN and Libris XL ID of objects that matched 1 Libris ISBN/ISSN", type=str)
parser.add_argument("badnomatch", help="Output FOLIO instance UUID, ISBN/ISSN and Libris XL ID(s) of objects that matched 0 or > 1Libris ISBN/ISSN", type=str)

args = parser.parse_args()

'''
Returns a list of all the values in a certain field's subfield (eg all 020 $a) 
'''
def get_subfield_values(record, field_code, subfield_code):
    all_subfield_values = []
    marc_record = record["fields"]
    for field in marc_record:
        if field_code in field:
            try:
                subfields = field[field_code]["subfields"]
                for subfield in subfields: 
                    subfield_value = subfield[subfield_code]
                    if subfield_value not in all_subfield_values:
                        all_subfield_values.append(subfield_value)
            except KeyError as k1:
                errors.append(f"Subfield object or subfield code {k1} missing for:\n {record}")
                continue
    return all_subfield_values


'''
Returns an ISN with with non-numeric characters other than "-" and "x" stripped off
''' 
def clean_isn(isn):
    clean_isn = re.sub('[^0-9x-]','', isn)
    return clean_isn

'''
Make a GET request to the Libris XL API anbd return the response
'''
def make_get_request(value, field):
    url = f"https://libris.kb.se/find.json?identifiedBy.value={value}&identifiedBy.@type={field}&@type=Instance"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Request failed for {value}. {response.text}\n")
        else:
            return response
    except HTTPError:
        print(f"Request failed for {value}. {response.text}\n")

'''
Get the Libris XL ID from every item in a parsed JSON response
'''
def get_libris_matches(json_response):
    for item in parsed_response["items"]:
        xl_id = item["@id"]
        if xl_id not in object.matched_xl_ids:
            object.matched_xl_ids.append(xl_id)

'''
Identify matching records and store IDs to corresponding lists
'''
def sort_and_document_matches(linked_ids, isn_type_matched):
    #Add matching XL ids from the response to the object
    if len(linked_ids[2]) == 1:
        if linked_ids not in isn_type_matched:
            isn_type_matched.append(linked_ids)
    elif len(linked_ids[2]) > 1:
        if linked_ids not in too_many_matches:
            too_many_matches.append(linked_ids)
    else:
        if linked_ids not in no_isn_match:
            no_isn_match.append(linked_ids)

# Define a class for a "match object", which contains FOLIO instance UUID, ISBN and ISSN (and could be extended with title, author, normalized versions of various values etc)
# TODO Add other matchable data like title 

class MatchObject:
      def __init__(self, record):
          self.folio_inst_id = get_subfield_values(record, "999", "i")
          self.isbn = get_subfield_values(record, "020", "a")
          self.issn = get_subfield_values(record, "022", "a")
          self.matched_xl_ids = []
          self.linked_ids = [self.folio_inst_id]

# Set up some variables to store data in
match_objects = []
errors = []
no_isn = []
has_isbn = []
has_issn = []
has_both = []
isbn_matched = []
issn_matched = []
no_isn_match = []
too_many_matches = []

#Initiate counters to keep track of progress
num_records = 0
start = time.time()

# Open a file containing FOLIO MARC records and start working with the data!
with open(args.infile) as f1:
    local_records = json.load(f1)

    for record in local_records:
        object = MatchObject(record)
        match_objects.append(object)
        
        # Decide on further actions depending on whether the record has 1) neither ISBN nor ISSN, 2) an ISBN, but no ISSN, 3) an ISSN, but no ISBN, 4) both ISBN and ISSN

        # Add to a list of records with no ISN. In the future it would be fun TODO to try to match on title etc instad
        if (not object.isbn) and (not object.issn):
            no_isn.extend(object.folio_inst_id)
        
        # Find out if there is a Libris XL record with matching ISBN
        elif object.isbn and not object.issn:
            has_isbn.append(object)
            object.linked_ids.append(object.isbn)

            for isbn in object.isbn:
                clean_isbn = clean_isn(isbn)
                libris_response = make_get_request(clean_isbn, "ISBN")
                time.sleep(0.01)
                parsed_response = libris_response.json()

                get_libris_matches(parsed_response)
                object.linked_ids.append(object.matched_xl_ids)
     
            sort_and_document_matches(object.linked_ids, isbn_matched)

        # Find out if there is a Libris XL record with matching ISSN
        elif object.issn and not object.isbn:
            has_issn.append(object)
            object.linked_ids.append(object.issn)

            for issn in object.issn:
                clean_issn = clean_isn(issn)
                libris_response = make_get_request(clean_issn, "ISSN")
                time.sleep(0.01)
          
                parsed_response = libris_response.json()

                get_libris_matches(parsed_response)
                object.linked_ids.append(object.matched_xl_ids)
     
            sort_and_document_matches(object.linked_ids, issn_matched)
                
        # Exempt from the matching procedure, add to a list and let a cataloguer have a look.
        else:
            if object.folio_inst_id not in has_both:
                has_both.append(object.folio_inst_id)    

        #Track progress and speed going through the items on the list
        num_records += 1
        if num_records % 2000 == 0:
            print("{} recs/s\t{}".format(
                round(num_records/(time.time() - start)),
                num_records), flush=True)

# Print the results to some files
with open(args.stats, "a") as f2, open(args.noissn, "a") as f3, open(args.isnmatch, "a") as f4, open(args.badnomatch, "a") as f5: 
    print("First some statistics:\n",file=f2)
    print("Total number of records:", len(match_objects), file=f2)
    print("Records with no ISN:", len(no_isn), file=f2)
    print("Records with ISBN:", len(has_isbn), file=f2)
    print("Records with ISSN:", len(has_issn), file=f2)
    print(f"Records with ISBN and ISSN: {len(has_both)}\n", file=f2)    
    print(f"\nTried to match {len(has_isbn) + len(has_issn)} against Libris XL. Now for the results!", file=f2)
    print("ISBN matches 1 Libris record:", len(isbn_matched), file=f2)
    print("ISSN matches 1 Libris record:", len(issn_matched), file=f2)
    print("ISBN/ISSN matched 0 Libris records:", len(no_isn_match), file=f2)
    print("ISBN/ISSN matches >1 Libris records:", len(too_many_matches), file=f2)

    print("\nNumer of errors identified:", len(errors), file=f2)
    print("\nErrors:\n", *errors, "\nStrange record identified by both ISBN and ISSN:\n", *has_both, sep="\n", file=f2)
    print("These FOLIO instances have no ISN to match on:\n", no_isn, file=f3)
    print("ISBN matched 1 Libris record:\n", *isbn_matched, "\n\nISSN matched 1 Libris record:\n", *issn_matched, sep="\n", file=f4)
    print("ISN matched 0 Libris records:\n", *no_isn_match, "\n\nISN matched >1 Libris records:\n", *too_many_matches, sep="\n", file=f5)