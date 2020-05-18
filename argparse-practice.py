import argparse
parser = argparse.ArgumentParser()
parser.add_argument("file", help="A file to analyze", type=str)
parser.add_argument("value", help="A value to search for", type=str)
args = parser.parse_args()
print(args.file, args.value)