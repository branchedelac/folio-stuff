#WIP

# [
#     {"001": "FOLIOstorage"}, 
#     {"008": "                                        "}, 
#     {"245": {"ind1": " ", "ind2": " ", "subfields": [{"a": "Verksamhetsberättelse :"}, {"b": "Biennial report 1994-1996/"}, {"c": "Onsala space observatory"}]}}, 
#     {"250": {"ind1": " ", "ind2": " ", "subfields": [{"a": "1996"}]}}, 
#     {"260": {"ind1": " ", "ind2": " ", "subfields": [{"c": "1996"}]}}, 
#     {"300": {"ind1": " ", "ind2": " ", "subfields": [{"a": "99 s."}]}}, 
#     {"710": {"ind1": "2", "ind2": " ", "subfields": [{"a": "Chalmers tekniska högskola."}, {"b": "Institutionen för radio- och rymdvetenskap"}]}}, 
#     {"907": {"ind1": " ", "ind2": " ", "subfields": [{"a": ".b11562444"}, {"b": "hbib "}, {"c": "s"}]}}, 
#     {"902": {"ind1": " ", "ind2": " ", "subfields": [{"a": "190628"}]}}, 
#     {"998": {"ind1": " ", "ind2": " ", "subfields": [{"b": "0"}, {"c": "      "}, {"d": "m"}, {"e": "b  "}, {"f": "s"}, {"g": "0"}]}}, 
#     {"945": {"ind1": " ", "ind2": " ", "subfields": [{"l": "hbib4"}, {"a": "Tp Chalmers tekniska högskola. Årsrapporter"}]}}, 
#     {"999": {"ind1": "f", "ind2": "f", "subfields": [{"i": "dcd1b847-bc46-4cb1-b906-fd8b7ac938d7"}]}}
# ]

# Read file, create dictionary with FOLIO UUID (999 $i) as key, and an list of identifiers as value

import json
import argparse
from operator import itemgetter 

parser = argparse.ArgumentParser()
parser.add_argument("file", help="A file to analyze", type=str)
args = parser.parse_args()

def get_subfield_value(record, field_code, subfield_code):
    for field in record:
        if field_code in field:
            subfields = field[field_code]["subfields"]
            if any(subfields): 
                for subfield in subfields:
                    subfield_value = subfield[subfield_code]
                    return subfield_value

class MatchObject:
      def __init__(self, record):
          self.folio_uuid = get_subfield_value(marc_fields, "999", "i")
          self.isbn = get_subfield_value(marc_fields, "020", "a")
          self.issn = get_subfield_value(marc_fields, "022", "a")

match_objects = []

with open(args.file) as a:
    local_records = json.load(a)

    for record in local_records[10000:10003]:
        marc_fields = record["fields"]
        object = MatchObject(marc_fields)
        match_objects.append(object)

for object in match_objects:
    print(object.isbn)


    # # Create an empty dictionary
    # record_ids = {}

    # for record_object in local_records[10000:10003]:
    #     # Dig down to the marc data
    #     marc_record = record_object["fields"]

    #     # Access the value in MARC 999 $i, and store it in a variable folio_uuid
    #     folio_uuid = get_subfield_value(marc_record, "999", "i")


    #     # Create an empty list to store ISN's in
    #     isns = []
    #     # Access the value in MARC 020 $a and MARC 022 $a, normalize it and store them in isbn and issn
    #     isbn = get_subfield_value(marc_record, "020", "a")
    #     if isbn is not None:
    #         isns.append(isbn)
    #     issn = get_subfield_value(marc_record, "022", "a")
    #     if issn is not None:
    #         isns.append(issn)


    #     # Add a key value pair to dict record_ids
    #     record_ids[folio_uuid] = isns



