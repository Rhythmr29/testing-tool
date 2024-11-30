import os
import subprocess
import shutil
import glob

# Get username input from the user
username = input("Enter the username to search: ")

# Define output directories and filenames
output_dir = "./combined_output"
json_output_file = os.path.join(output_dir, f"{username}_combined_output.json")

# Ensure the combined output directory exists
os.makedirs(output_dir, exist_ok=True)

commands = [
    {
        "command": (
            f"bash -c 'cd maigret && source venv/bin/activate && "
            f"maigret {username} --json simple --folderoutput .{output_dir} && deactivate'"
        ),
        "output_file": f".{output_dir}/maigret_{username}.json"
    },
    {
        "command": f"cd sherlock && sherlock {username} --print-found --csv",
        "output_file": f"sherlock/{username}.csv",
        "move_to": os.path.join(output_dir, f"{username}.csv")
    },
    {
        "command": (
            f"bash -c 'cd socialscan && source venv/bin/activate && "
            f"socialscan {username} --json socialscan_{username}.json && deactivate'"
        ),
        "output_file": f"socialscan/socialscan_{username}.json",
        "move_to": os.path.join(output_dir, f"socialscan_{username}.json")
    },
    {
        "command": (
            f"bash -c 'cd blackbird && source venv/bin/activate && "
            f"python3 blackbird.py -u {username} --csv && deactivate'"
        ),
        "output_pattern": f"blackbird/results/{username}_*/{username}_*.csv",  # Pattern for blackbird output
        "move_to": os.path.join(output_dir, f"blackbird_{username}.csv")
    }
]

def run_command(command):
    try:
        print(f"Running command: {command}")
        subprocess.run(command, shell=True, check=True)
        print("Command completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")

def move_file(source, destination):
    if os.path.exists(source):
        shutil.move(source, destination)
        print(f"Moved {source} to {destination}")
    else:
        print(f"Error: Expected output file {source} not found.")

# Run each command and move output files
for cmd in commands:
    run_command(cmd["command"])
    
    # Move Sherlock output to combined folder immediately after it is created
    if "output_file" in cmd and "move_to" in cmd:
        move_file(cmd["output_file"], cmd["move_to"])

    # For Blackbird, use a glob pattern to find the actual CSV file
    elif "output_pattern" in cmd:
        matches = glob.glob(cmd["output_pattern"])
        if matches:
            for match in matches:
                move_file(match, cmd["move_to"])

print(f"All output files have been moved to {output_dir}")
