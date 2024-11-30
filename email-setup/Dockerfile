# Use Ubuntu as the base image
FROM ubuntu:20.04

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory inside the container
WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    virtualenv \
    git \
    curl \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Clone and set up Breach-Checker
RUN git clone https://github.com/x404xx/Breach-Checker.git
WORKDIR /app/Breach-Checker
RUN virtualenv env && \
    . env/bin/activate && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install httpx user_agent && \
    deactivate

# Clone and set up Holehe
WORKDIR /app
RUN git clone https://github.com/megadose/holehe.git
WORKDIR /app/holehe
RUN virtualenv env && \
    . env/bin/activate && \
    python3 setup.py install && \
    pip install requests && \
    deactivate


# Clone and set up BreachCheck
WORKDIR /app
RUN git clone https://github.com/v4resk/BreachCheck.git
WORKDIR /app/BreachCheck
RUN virtualenv env && \
    . env/bin/activate && \
    pip install --no-cache-dir -r requirements.txt && \
    deactivate
RUN sed -i 's/"BreachedDirectory":".*"/"BreachedDirectory":"34ae91f046msh7c96d1b59686d33p1e4cd6jsna32a8d24cc9a"/' conf.json

# Copy the script files into the container
WORKDIR /app
COPY EScript3.py final_op2.py finalScript.py /app/

# Create Combined_folder for output files
RUN mkdir /app/Combined_folder

# Set permissions to make scripts executable
RUN chmod +x /app/EScript3.py /app/final_op2.py /app/finalScript.py

# Debugging Step: List all files to confirm environment setup
RUN ls -R /app

# Run finalScript.py as the container entry point
ENTRYPOINT ["/bin/bash", "-c", "source /app/Breach-Checker/env/bin/activate && python3 /app/finalScript.py"]


# to build and run this docker file 
# docker build -t email-setup .     
# docker run --rm -e EMAIL="rhythmtom29@gmail.com" -v "/c/Users/sacha/OneDrive/Desktop/SGP7/Combined_folder:/app/Combined_folder" email-setup
