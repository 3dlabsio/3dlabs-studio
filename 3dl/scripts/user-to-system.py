#!/usr/bin/env python

import json
import sys

def merge_json(json1, json2):
    # Load the JSON data
    json1_data = json.load(json1)
    json2_data = json.load(json2)

    # Merge the two dictionaries, keeping the value of the "inherits" key from the first file if it exists
    merged_data = {**json1_data, **json2_data}
    if "inherits" in json1_data:
        merged_data["inherits"] = json1_data["inherits"]

    # Check for the "type" and "from" keys
    if "type" in merged_data and merged_data["type"] == "filament" and "from" in merged_data and merged_data["from"] == "User":
        # Change the value of the "from" key
        merged_data["from"] = "system"

    # Remove the "pressure_advance" key if its value is 0 in the second file
    if "pressure_advance" in json2_data and json2_data["pressure_advance"] == 0:
        merged_data.pop("pressure_advance", None)

    # Sort the keys under the "header" by alphabetical order
    header_keys = ["type", "filament_id", "setting_id", "name", "from", "instantiation", "inherits", "filament_vendor", "compatible_prints"]
    sorted_data = {k: merged_data[k] for k in sorted(merged_data) if k in header_keys}
    sorted_data.update({k: merged_data[k] for k in sorted(merged_data) if k not in header_keys})

    # Return the sorted data as a JSON string
    return json.dumps(sorted_data, indent=4)

# Check if the required number of arguments was provided
if len(sys.argv) != 3:
    print("Usage: python merge_json.py file1.json file2.json")
    sys.exit(1)

# Get the filenames from the command line arguments
json1_filename = sys.argv[1]
json2_filename = sys.argv[2]

# Create the output filename by adding "_merged" to the first filename
output_filename = json1_filename[:-5] + "_merged.json"

with open(json1_filename, 'r') as json1, open(json2_filename, 'r') as json2:
    # Merge the files and store the result in a variable
    merged = merge_json(json1, json2)

# Write the merged data to the output file
with open(output_filename, 'w') as output_file:
    output_file.write(merged)

# Print a message indicating that the file was written successfully
print(f"Merged data written to {output_filename}")


