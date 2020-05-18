import sys
import json
import argparse
from gooey import Gooey

@Gooey
def user_input():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="A file to search through", type=str)
    parser.add_argument("value", help="The value we're looking for", type=str)
    args = parser.parse_args()

    input = vars(args)

    return input

def find_value(user_input):
    input = user_input()
    file = input['file']
    value = input['value']

    print(f"Let's start searching through {file} to find records containing the value {value}.\n---\n")

    with open(file, 'rb') as json_records:
        read_records = json.load(json_records)
        matches = []
        for record in read_records:
            body = str(record)
            if value in body:
                matches.append(body)
                print(f"Found a record containing the value {value}. Check it out below: \n\n {body}")
        if len(matches) == 0: 
            print(f"\nThe value {value} is not present in the file {file}.")
    
    print(f"\n---\nAll in all, we found {len(matches)} occurences of {value} in {file}.")
                
#Run function
find_value(user_input)