import os
import csv
import json

# Define folder and output path
input_folder = "/app/Combined_folder"  # Ensure absolute path for Docker consistency
output_file = os.path.join(input_folder, "final_output.json")  # Save directly to Combined_folder

# Initialize a dictionary to hold the combined data
combined_data = {}

# Function to convert CSV to JSON
def csv_to_json(csv_file_path):
    data = []
    with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data.append(row)
    return data

# Function to clean malformed JSON
def clean_malformed_json(file_path):
    corrected_data = []
    with open(file_path, mode='r', encoding='utf-8') as json_file:
        buffer = ""
        for line in json_file:
            buffer += line.strip()  # Combine lines into a buffer
            try:
                # Try parsing the current buffer
                parsed = json.loads(buffer)
                corrected_data.append(parsed)
                buffer = ""  # Clear the buffer after successful parse
            except json.JSONDecodeError:
                # If parsing fails, continue adding to the buffer
                pass
    return corrected_data

# Function to process JSON files
def process_json_file(file_path):
    try:
        with open(file_path, mode='r', encoding='utf-8') as json_file:
            # Try loading as a single JSON object
            return json.load(json_file)
    except json.JSONDecodeError:
        # If it fails, attempt to clean malformed JSON
        print(f"Attempting to clean malformed JSON in {file_path}")
        return clean_malformed_json(file_path)

# Process all files in the input folder
for filename in os.listdir(input_folder):
    file_path = os.path.join(input_folder, filename)
    
    if filename.endswith(".csv"):
        try:
            csv_data = csv_to_json(file_path)
            combined_data[filename] = csv_data
        except Exception as e:
            print(f"Error processing CSV file {filename}: {e}")
    
    elif filename.endswith(".json"):
        try:
            json_data = process_json_file(file_path)
            if json_data:
                combined_data[filename] = json_data
        except Exception as e:
            print(f"Error processing JSON file {filename}: {e}")

# Ensure the Combined_folder exists before saving
if not os.path.exists(input_folder):
    os.makedirs(input_folder)

# Save the combined data to the output JSON file
try:
    with open(output_file, mode='w', encoding='utf-8') as output_json_file:
        json.dump(combined_data, output_json_file, indent=4)
    print(f"Combined data with filenames has been written to {output_file}")
except Exception as e:
    print(f"Error writing to output file: {e}")
