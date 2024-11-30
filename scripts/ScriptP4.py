import json
import re
import subprocess
import os

# Directory for storing individual tool outputs
output_directory = './phone_outputs/'
os.makedirs(output_directory, exist_ok=True)

# Check if Phunter directory exists
phunter_dir = os.path.abspath("Phunter")
if not os.path.isdir(phunter_dir):
    print(f"The 'Phunter' directory was not found at {phunter_dir}. Please ensure it is in the correct location.")
    exit()

# Function to validate the phone number format and length
def validate_phone_number(phone_number):
    # Basic validation: starts with +, followed by country code and number
    if re.match(r'^\+\d{10,15}$', phone_number):
        return True
    else:
        print("Invalid phone number format. Ensure it starts with '+' followed by country code and 10-15 digits.")
        return False

# Function to remove ANSI escape sequences from output
def clean_ansi_sequences(text):
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

# Function to replace specific unwanted Unicode characters and emoji with text equivalents
def replace_unicode_symbols(line):
    # Replace Unicode box drawing and emoji symbols with textual equivalents
    replacements = {
        "\u251c\u2500\u2500": "-->",     # box drawing for branching
        "\u2514\u2500\u2500": "-->",     # box drawing for end branch
        "\u2714": "Valid",               # check mark symbol
        "\ud83d\udcde": "Phone Number:", # telephone receiver emoji
        "\ufe0f": "",                    # variation selector (remove if found)
    }
    for unicode_char, replacement in replacements.items():
        line = line.replace(unicode_char, replacement)
    return line

def filter_unwanted_data(lines):
    filtered_lines = []
    unwanted_patterns = [
        r'^\s*[_]+',                       # ASCII art lines
        r'^\s*[\(\)]',                     # Lines with parentheses only
        r'^`-.-\' \\\)\\-\`\\( , o o\\)',  # ASCII face patterns
        r'^`-    \\\`_`\"\'-',             # ASCII arm/branch
        r'^`-\(-\'$',                      # ASCII bottom line
        r'by Norze',                       # Branding info
        r'^\|\s*Phone number OSINT Tool\s*\|$',  # Branding line
        r'^:.*:$'                          # Header lines with only colons
    ]

    # Compile patterns into regex objects
    regex_patterns = [re.compile(pattern) for pattern in unwanted_patterns]

    for line in lines:
        line = line.strip()
        # Skip lines matching any unwanted pattern
        if any(regex.match(line) for regex in regex_patterns):
            continue
        # Replace specific Unicode symbols with text equivalents
        line = replace_unicode_symbols(line)
        filtered_lines.append(line)
    
    return filtered_lines

# Function to format output by grouping URLs and other results into sections
def format_output(output_text):
    sections = {}
    current_section = None

    filtered_lines = filter_unwanted_data(output_text.splitlines())

    for line in filtered_lines:
        if "Results for" in line or "Social media" in line:
            current_section = line.strip().replace("Results for ", "").replace(":", "")
            sections[current_section] = []
        elif line.startswith("URL:") and current_section:
            sections[current_section].append(line.strip())
        elif line.strip():
            if current_section:
                sections[current_section].append(line.strip())
            else:
                sections["General"] = sections.get("General", []) + [line.strip()]
    return sections

# Prompt user for the phone number
phone_number = input("Enter the phone number (with country code, e.g., +919726600474): ")

# Validate the phone number
if not validate_phone_number(phone_number):
    exit("Phone number is invalid. Please try again with a valid number.")

# Define tool commands and expected output paths
tools = {
    "phoneinfoga": {
        "command": f"NUMVERIFY_API_KEY=eGNYXAZqCxQfjJBfrbOjRIMzIT3mYHMC phoneinfoga scan -n {phone_number} > {output_directory}/phoneinfoga_output.txt",
        "output_file": f"{output_directory}/phoneinfoga_output.txt"
    },
    "phunter": {
        # Use direct path to activate virtual environment
        "command": f"cd {phunter_dir} && . venv/bin/activate && python3 phunter.py -t {phone_number} > ../{output_directory}/phunter_output.txt && deactivate",
        "output_file": f"{output_directory}/phunter_output.txt"
    }
}

# Run each tool and capture the output
for tool_name, config in tools.items():
    print(f"Running {tool_name}...")
    try:
        result = subprocess.run(config["command"], shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running {tool_name}: {result.stderr}")
        else:
            print(f"{tool_name} completed successfully.")
    except Exception as e:
        print(f"Exception occurred while running {tool_name}: {str(e)}")

# Function to load tool output and convert it to JSON if needed, cleaning ANSI sequences if text
def load_output_as_json(output_file):
    try:
        with open(output_file, 'r') as f:
            content = f.read()
            # Try parsing as JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # If not JSON, treat as plain text, clean it, and format as JSON
                cleaned_content = clean_ansi_sequences(content)
                formatted_content = format_output(cleaned_content)
                return formatted_content
    except FileNotFoundError:
        print(f"File {output_file} not found.")
        return {"error": "Data not available or failed to load."}

# Function to clean and format JSON data for readability
def format_json(data):
    # Convert data to a well-structured JSON format
    return json.dumps(data, indent=4, sort_keys=True)

# Consolidate all results into a single JSON structure
consolidated_data = {
    "phone_number": phone_number,
    "tools_results": {}
}

# Load each tool's output and add it to the consolidated data
for tool_name, config in tools.items():
    tool_data = load_output_as_json(config["output_file"])
    consolidated_data["tools_results"][tool_name] = tool_data

# Format the consolidated data for readability
formatted_data = format_json(consolidated_data)

# Output formatted consolidated data to a single JSON file
output_file = f"{phone_number}.json"
with open(output_file, 'w') as f:
    f.write(formatted_data)

print(f"Consolidated and formatted results saved to {output_file}")

