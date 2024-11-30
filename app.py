from flask import Flask, request, jsonify, send_from_directory, render_template
import subprocess
import os
import json

app = Flask(__name__, static_folder="static", template_folder="static")

# Mapping entities to their Docker container details
DOCKER_CONTAINERS = {
    "email": {
        "image": "email-setup",
        "output_dir": "./email-setup/Combined_folder/",
        "command": lambda input_value: [
            "docker", "run", "--rm", "-e", f"EMAIL={input_value}", "-v",
            f"{os.path.abspath('./email-setup/Combined_folder')}:/app/Combined_folder", "email-setup"
        ]
    },
    "phone": {
        "image": "phoneinfo-tool",
        "output_dir": "./phoneinfo-setup/phonenum_op/",
        "command": lambda input_value: [
            "docker", "run", "--rm", "-e", f"PHONE_NUMBER={input_value}", "-v",
            f"{os.path.abspath('./phoneinfo-setup/phonenum_op')}:/app/output", "phoneinfo-tool"
        ]
    },
    "username": {
        "image": "username-setup",
        "output_dir": "./username-setup/username_op/",
        "command": lambda input_value: [
            "docker", "run", "--rm", "-e", f"USERNAME={input_value}", "-v",
            f"{os.path.abspath('./username-setup/username_op')}:/app/combined_output", "username-setup"
        ]
    }
}

# Serve the HTML file
@app.route("/")
def serve_index():
    return render_template("index.html")

# Endpoint to fetch entity data
@app.route("/fetch-entity-data", methods=["POST"])
def fetch_entity_data():
    try:
        # Parse request JSON
        data = request.get_json()
        entity = data.get("entity")
        input_value = data.get("inputValue")

        if not entity or not input_value:
            return jsonify({"error": "Entity and input value are required"}), 400

        # Get the corresponding Docker container details
        container_details = DOCKER_CONTAINERS.get(entity)
        if not container_details:
            return jsonify({"error": "Invalid entity selected"}), 400

        # Generate the Docker command
        docker_command = container_details["command"](input_value)

        # Run the Docker container with the correct command
        process = subprocess.run(
            docker_command,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8"  # Ensure UTF-8 encoding
        )
        print(f"Docker command output: {process.stdout}")

        # Handle output JSON file path
        output_dir = container_details["output_dir"]
        if entity == "phone":
            # Dynamically generate output file name for phone
            json_file_path = os.path.join(output_dir, f"{input_value}.json")
        else:
            # Predefined file names for email and username
            json_file_path = os.path.join(output_dir, "final_output.json")

        # Check if the output file exists
        if not os.path.exists(json_file_path):
            return jsonify({"error": f"No output file found for {entity}"}), 500

        # Read and return the JSON file contents
        with open(json_file_path, "r", encoding="utf-8") as file:
            output_data = json.load(file)

        return jsonify(output_data)

    except subprocess.CalledProcessError as e:
        # Log the error details and return an error response
        error_message = e.stderr if e.stderr else str(e)
        print(f"Error running Docker: {error_message}")
        return jsonify({"error": f"Error running Docker: {error_message}"}), 500
    except Exception as e:
        # General error handling
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
