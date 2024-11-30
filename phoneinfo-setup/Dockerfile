# Base image
FROM ubuntu:20.04

# Set non-interactive mode for apt-get to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory inside the container
WORKDIR /app

# Update and install necessary system dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv git curl bash wget tar && \
    apt-get clean

# Install PhoneInfoga globally
RUN bash -c "curl -sSL https://raw.githubusercontent.com/sundowndev/phoneinfoga/master/support/scripts/install | bash" && \
    install ./phoneinfoga /usr/local/bin/phoneinfoga && \
    phoneinfoga version

# Clone and set up Phunter using the N0rz3 repository
RUN git clone https://github.com/N0rz3/Phunter.git /app/Phunter && \
    cd /app/Phunter && \
    python3 -m venv venv && \
    bash -c "source venv/bin/activate && pip3 install -r requirements.txt"

# Copy the script into the container
COPY script.py /app/script.py

# Expose the required port for Phunter or other tools if needed (optional)
EXPOSE 8000

# Set the default command to run the script
CMD ["python3", "/app/script.py"]


# to build this dockerfile image 
# docker build -t phoneinfo-tool .                      

# to run this docker file 
# docker run -it --rm -v "C:\Users\sacha\OneDrive\Desktop\SGP7:/app/output" phoneinfo-tool
