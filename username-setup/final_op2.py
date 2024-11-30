import os
import csv
import json

# Define folder and output path
input_folder = "combined_output"  # Adjusted folder name
output_file = "final_output.json"

# Initialize a dictionary to hold the combined data with filenames as keys
combined_data = {}

# Function to convert CSV to JSON format
def csv_to_json(csv_file_path):
    data = []
    with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data.append(row)
    return data

# Loop through each file in the input folder
for filename in os.listdir(input_folder):
    file_path = os.path.join(input_folder, filename)
    
    # Check if the file is a CSV file
    if filename.endswith(".csv"):
        # Convert CSV to JSON and add to combined data under filename as key
        csv_data = csv_to_json(file_path)
        combined_data[filename] = csv_data

    # Check if the file is a JSON file
    elif filename.endswith(".json"):
        # Load JSON data and add to combined data under filename as key
        with open(file_path, mode='r', encoding='utf-8') as json_file:
            json_data = json.load(json_file)
            combined_data[filename] = json_data

# Save the combined data to the final JSON output file
with open(output_file, mode='w', encoding='utf-8') as output_json_file:
    json.dump(combined_data, output_json_file, indent=4)

print(f"Combined data with filenames has been written to {output_file}")
