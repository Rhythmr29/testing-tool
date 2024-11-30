import subprocess

# Define the paths to both scripts
script3_path = "./EScript3.py"
final_op2_path = "./final_op2.py"

def run_script(script_path):
    try:
        print(f"Running script: {script_path}")
        subprocess.run(["python3", script_path], check=True)
        print(f"Script {script_path} completed successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script_path}: {e}")

# Run Script3.py
run_script(script3_path)

# Run final_op2.py
run_script(final_op2_path)

print("All scripts have completed execution.")
