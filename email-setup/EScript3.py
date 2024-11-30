import subprocess
import re
import os
import pty
import time
import shutil
import argparse


def is_valid_email(email):
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)


def run_command_with_input(command, input_data=None, stop_after=5):
    """Run a shell command in a pseudo-terminal, send input, and stop it after some time."""
    try:
        master, slave = pty.openpty()  # Create a pseudo-terminal
        process = subprocess.Popen(
            command,
            shell=True,
            stdin=slave,
            stdout=master,
            stderr=subprocess.PIPE,
            text=True
        )

        if input_data:
            os.write(master, input_data.encode())  # Send input

        time.sleep(stop_after)  # Wait before terminating
        process.terminate()
        process.wait()

        # Read output from the pseudo-terminal
        os.close(slave)
        output = os.read(master, 4096).decode("utf-8")
        os.close(master)

        if process.returncode != 0:
            print(f"Error running command: {command}\nError Details:\n{process.stderr.read()}")
        return output
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)


def run_command_without_terminal(command):
    """Run a command without using a pseudo-terminal and capture its output."""
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            print(f"Error running command: {command}\nError Details:\n{stderr}")
        return stdout
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)


def check_and_prepare_tool(tool_dir, tool_name):
    """Check if a tool directory exists and its virtual environment is set up."""
    if not os.path.isdir(tool_dir):
        print(f"Error: Directory '{tool_dir}' for {tool_name} does not exist.")
        exit(1)

    venv_path = os.path.join(tool_dir, "env", "bin", "activate")
    if not os.path.isfile(venv_path):
        print(f"Error: Virtual environment for '{tool_name}' not found in '{tool_dir}'. Please set it up first.")
        exit(1)


def move_file_to_combined_folder(source_file, combined_folder):
    """Move a file to the Combined_folder."""
    if not os.path.exists(combined_folder):
        os.makedirs(combined_folder)  # Create the folder if it doesn't exist
    if os.path.isfile(source_file):
        shutil.move(source_file, combined_folder)
        print(f"Moved {source_file} to {combined_folder}")
    else:
        print(f"Warning: File {source_file} does not exist and could not be moved.")


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run email-based security tools.")
    parser.add_argument(
        "--email", type=str, required=False,
        default=os.getenv("EMAIL"),
        help="Email address to use with the tools. Can also be set via EMAIL environment variable."
    )
    args = parser.parse_args()

    email = args.email

    if not email or not is_valid_email(email):
        print("Error: A valid email address is required. Provide it via --email or EMAIL environment variable.")
        exit(1)

    combined_folder = "/app/Combined_folder"  # Common folder to store output files

    # Tool 1: Breach-Checker
    tool1_dir = "/app/Breach-Checker"
    check_and_prepare_tool(tool1_dir, "Breach-Checker")  # Pass both arguments
    print("Running Breach-Checker...")
    try:
        command = (
            f"bash -c 'cd {tool1_dir} && source env/bin/activate && "
            f"python -m bchecker -m 1 -e \"{email}\" && deactivate'"
        )
        output = run_command_with_input(command, input_data="y\ny\n", stop_after=5)
        print(f"Breach-Checker Output:\n{output}")

        # Move the output file to Combined_folder
        breach_checker_output = os.path.join(tool1_dir, "mailleaks.json")
        move_file_to_combined_folder(breach_checker_output, combined_folder)

    except Exception as e:
        print(f"Failed to run Breach-Checker: {e}")

    # Tool 2: Holehe
    tool2_dir = "/app/holehe"
    check_and_prepare_tool(tool2_dir, "Holehe")  # Pass both arguments
    print("Running Holehe...")
    try:
        command = (
            f'bash -c "cd \\"{tool2_dir}\\" && source env/bin/activate && '
            f'holehe {email} --only-used -C && deactivate"'
            )
        output = run_command_without_terminal(command)
        print(f"Holehe Output:\n{output}")

        # Dynamically find the latest output file matching the naming pattern
        holehe_output_file = None
        for file in os.listdir(tool2_dir):
            if file.startswith("holehe_") and file.endswith("_results.csv"):
                file_path = os.path.join(tool2_dir, file)
                if holehe_output_file is None or os.path.getmtime(file_path) > os.path.getmtime(holehe_output_file):
                    holehe_output_file = file_path

        # Move the output file to Combined_folder
        if holehe_output_file:
            move_file_to_combined_folder(holehe_output_file, combined_folder)
        else:
            print("Warning: Holehe output file not found.")

    except Exception as e:
        print(f"Failed to run Holehe: {e}")

    # Tool 3: BreachCheck
    tool3_dir = "/app/BreachCheck"
    check_and_prepare_tool(tool3_dir, "BreachCheck")  # Pass both arguments
    print("Running BreachCheck...")
    try:
        command = (
            f"bash -c 'cd {tool3_dir} && source env/bin/activate && "
            f"python BreachCheck.py -t {email} -oR {email}.json && deactivate'"
        )
        output = run_command_without_terminal(command)
        print(f"BreachCheck Output:\n{output}")

        # Move the output file to Combined_folder
        breach_check_output = os.path.join(tool3_dir, f"{email}.json")
        move_file_to_combined_folder(breach_check_output, combined_folder)

    except Exception as e:
        print(f"Failed to run BreachCheck: {e}")


if __name__ == "__main__":
    main()
