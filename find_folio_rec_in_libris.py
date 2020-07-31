#WIP

# Read file, create dictionary with FOLIO UUID (999 $i) as key, and an list of identifiers as value

import json
import argparse
import time
import requests
from requests.exceptions import HTTPError

parser = argparse.ArgumentParser()
parser.add_argument("infile", help="A file to analyze", type=str)
parser.add_argument("stats", help="Output statistics and results summary here", type=str)
parser.add_argument("noissn", help="Output a list of objects without ISSN", type=str)
parser.add_argument("isnmatch", help="Output FOLIO instance UUID, ISBN/ISSN and Libris XL ID of objects that matched 1 Libris ISBN/ISSN", type=str)
parser.add_argument("badnomatch", help="Output FOLIO instance UUID, ISBN/ISSN and Libris XL ID(s) of objects that matched 0 or > 1Libris ISBN/ISSN", type=str)

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
                    if subfield_value not in all_subfield_values:
                        all_subfield_values.append(subfield_value)
            except KeyError as k1:
                errors.append(f"Subfield object or subfield code{k1} missing for {record}")
                continue
    return all_subfield_values

# Define a function which makes a GET request to the Libris XL API
def make_get_request(value, field):
    url = f"https://libris.kb.se/find.json?identifiedBy.value={value}&identifiedBy.@type={field}&@type=Instance"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Request failed for {value}. {response.text}\n")
    else:
        return response

# Define a function which gets the Libris XL ID from every item ín a parsed JSON response 
def get_libris_matches(json_response):
    for item in parsed_response["items"]:
        xl_id = item["@id"]
        if xl_id not in  object.matched_xl_ids:
            object.matched_xl_ids.append(xl_id)

# Define a class for a "match object", which contains FOLIO instance UUID, ISBN and ISSN (and could be extended with title, author, normalized versions of various values etc)
# TODO Add other matchable data like title 

class MatchObject:
      def __init__(self, record):
          self.folio_inst_id = get_subfield_values(record, "999", "i")
          self.isbn = get_subfield_values(record, "020", "a")
          self.issn = get_subfield_values(record, "022", "a")
          self.matched_xl_ids = []

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

# Start working with the data

with open(args.infile) as f1:
    local_records = json.load(f1)

    for record in local_records:
        object = MatchObject(record)
        match_objects.append(object)
        
        # TODO Try to match on title etc
        if (not object.isbn) and (not object.issn):
            no_isn.extend(object.folio_inst_id)
        
        # If the record has an ISBN and no ISSN, we'll seacrh for that ISBN in Libris
        elif object.isbn and not object.issn:
            # First append the object to a list of records with ISBNs
            has_isbn.append(object)

            #For every ISBN, make a query to Libris to get the corresponding Libris instance
            for isbn in object.isbn:
                libris_response = make_get_request(isbn, "ISBN")
                time.sleep(0.01)
                
                #Parse the response as JSON
                parsed_response = libris_response.json()
                linked_ids = [object.folio_inst_id, object.isbn]

                # If totalItems > 0, the query returned at least one matching Libris instance. Only in this case will we go further into the response.
                if parsed_response["totalItems"] > 0:
                    #Add matching XL ids from the response to the object
                    get_libris_matches(parsed_response)
                    linked_ids.append(object.matched_xl_ids)

                    #If we only get one matching XL ID, we'll add the value at index 0 to the object's list of matching XL IDs (but we won't create duplicate values in the list).
                    if len(object.matched_xl_ids) == 1:
                        if linked_ids not in isbn_matched:
                            isbn_matched.append(linked_ids)
                    elif len(object.matched_xl_ids) > 1:
                        if linked_ids not in too_many_matches:
                            too_many_matches.append(linked_ids)
                    else:
                        print(f"{object.isbn} Very bad Libris record that does not have an ID! Error!")
                # If totalItems = 0, the query returned no matching Libris instances. Let's just note that this ISBN has no match.
                else:
                    if linked_ids not in no_isn_match:
                        no_isn_match.append(linked_ids)


        elif object.issn and not object.isbn:
            has_issn.append(object)
            for issn in object.issn:
                libris_response = make_get_request(issn, "ISSN")
                time.sleep(0.01)
          
                #Parse the response as JSON
                parsed_response = libris_response.json()
                linked_ids = [object.folio_inst_id, object.issn]

                # If totalItems > 0, the query returned at least one matching Libris instance. Only in this case will we go further into the response.
                if parsed_response["totalItems"] > 0:
                    #Add matching XL ids from the response to the object
                    get_libris_matches(parsed_response)
                    linked_ids.append(object.matched_xl_ids)

                    #If we only get one matching XL ID, we'll add the value at index 0 to the object's list of matching XL IDs (but we won't create duplicate values in the list).
                    if len(object.matched_xl_ids) == 1:
                        if linked_ids not in issn_matched:
                            issn_matched.append(linked_ids)
                    elif len(object.matched_xl_ids) > 1:
                        if linked_ids not in too_many_matches:
                            too_many_matches.append(linked_ids)
                    else:
                        print(f"{object.issn} Very bad Libris record that does not have an ID! Error!")
                # If totalItems = 0, the query returned no matching Libris instances. Let's just note that this ISBN has no match.
                else:
                    if linked_ids not in no_isn_match:
                        no_isn_match.append(linked_ids)
        else:
        # This is an edge case case, if they have both ISSN and ISBN, let's just print it so a cataloguer can have a look
            has_both.append(vars(object))
                

        #Track progress and speed going through the items on the list
        num_records += 1
        if num_records % 2000 == 0:
            print("{} recs/s\t{}".format(
                round(num_records/(time.time() - start)),
                num_records), flush=True)

# Print some results to a file
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

    print("\nAny errors?", file=f2)
    print("Numer of data errors:", len(errors), file=f2)
    print("\nErrors:\n", *errors, *has_both, sep="\n", file=f2)

    print("These FOLIO instances have no ISN to match on:\n", no_isn, file=f3)
    print("ISBN matched 1 Libris record:\n", *isbn_matched, "\n\nISSN matched 1 Libris record:\n", *issn_matched, sep="\n", file=f4)
    print("ISN matched 0 Libris records:\n", *no_isn_match, "\n\nISN matched >1 Libris records:\n", *too_many_matches, sep="\n", file=f5)