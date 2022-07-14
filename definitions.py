#!/opt/homebrew/bin/python3
"""
Invoke with the -a or --add flag to add an definitions:

$ ./definitions.py -a NASA
$ ./definitions.py --add IETF

You will then be prompted to fill in some details.

Invoke with the -l or --lookup flag to look up an existing definitions:

$ ./definitions.py -l CLI
$ ./definitions.py --lookup GUI
"""
 
import argparse
import json
import os
import re
import readline
import sys
import textwrap
from pathlib import Path

DEFINITIONS_FILE = Path(__file__).parent / "./definitions.json"
 
#-----------------------------------------------------------------------------
# Set up the options for argparse
#-----------------------------------------------------------------------------
 
parser = argparse.ArgumentParser(description="A script for looking up definitions.")
parser.add_argument('-a', '--add', dest='new_definitions',
    help="add a new definitions")
parser.add_argument('-l', '--lookup', metavar='DEFINITIONS',
    help="look up an existing definitions")
args = parser.parse_args()
 
#-----------------------------------------------------------------------------
# Utility functions
#-----------------------------------------------------------------------------
 
def read_definitions_file(definitions_file=DEFINITIONS_FILE):
    """Get a list of existing definitions from a JSON file, or create the file if 
    it does not exist.
    """
    if not os.path.isfile(definitions_file):
        with open(definitions_file, 'w') as outfile:
            outfile.write('[]')
            
    with open(definitions_file, 'r') as json_data:
        data = json.load(json_data)
    
    return data
 
def write_definitions_file(data, definitions_file=DEFINITIONS_FILE):
    """Write the list of definitions to a JSON file."""
    with open(definitions_file, 'w') as outfile:
        outfile.write(json.dumps(data))
 
def get_new_definitions(definitions=None):
    """Ask the user for information about the new definitions."""
    if definitions is None:
        definitions = input("What is the new definitions?\n")
    else:
        print("Creating an entry for definitions \"%s\"." % definitions)
    expansion   = input("\nWhat is \"%s\"?\n" % definitions)
    description = input("\nFull Description (optional)\n")
    example     = input("\nExample (optional)\n")
    result     = input("\nResult (optional)\n")
    
    new_definitions = {
        "definitions": definitions,
        "expansion": expansion,
        "example": example,
        "result": result
    }
    if description:
        new_definitions["description"] = description

    if description:
        new_definitions["example"] = example

    if description:
        new_definitions["result"] = result
    
    return new_definitions
 
def add_new_definitions(definitions):
    """Ask the user for the new definitions, and write it to file."""
    new_definitions = get_new_definitions(definitions)
    data        = read_definitions_file()
    data.append(new_definitions)
    write_definitions_file(data)
 
class color:
   BOLD = '\033[1m'
   END  = '\033[0m'
 
def print_definitions(entry):
    """Pretty print an definitions to the console.""" 
    print("")
    print(color.BOLD + entry["definitions"])
    print(entry["expansion"] + color.END)
    if "description" in entry:
        wrapper = textwrap.TextWrapper(initial_indent=" " * 4, width=100,
                                       subsequent_indent=" " * 4)
        print(wrapper.fill(entry["description"]))
    if "example" in entry:
        wrapper = textwrap.TextWrapper(width=200)
        print(wrapper.fill(entry["example"]))
    if "result" in entry:
        wrapper = textwrap.TextWrapper(width=200)
        print(wrapper.fill(entry["result"]))
    print("")
 
#-----------------------------------------------------------------------------
# Mainline program function
#-----------------------------------------------------------------------------
 
def main():
    
    # If no arguments are supplied, print the help message and exit
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    
    # If the --add flag is supplied, create a new definitions and write it out to
    # the database
    if args.new_definitions is not None:
        add_new_definitions(args.new_definitions)
    
    # If we're looking up an existing definitions, do a search on the list of
    # existing definitions
    if args.lookup is not None:
        data = read_definitions_file()
        matches = []
        
        for entry in data:
            
            # We include both a perfect match, and a match on just the letters
            # so 'abc' matches 'A-BC'. It doesn't coerce Unicode chars to their
            # ASCII counterparts, but I also don't use any definitions that include
            # accented characters.
            possible_matches = [
                entry["definitions"].lower(),
                re.sub('[^a-z]', '', entry["definitions"].lower())
            ]
            
            if args.lookup.lower() in possible_matches:
                matches.append(entry)
        
        for entry in sorted(matches, key=lambda entry: entry["expansion"]):
            print_definitions(entry)
        
        # If we haven't found the definitions, offer to create it
        if not matches:
            create = input("No definition. Would you like to create it? [y/N]\n")
            if create.lower() in ['y', 'yes']:
                add_new_definitions(args.lookup)
            else:
                print("Okay, never mind.")
        
if __name__ == '__main__':
    main()