# Use the latest Ubuntu stable build
FROM ubuntu:latest

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies for Python and virtual environment
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Create and activate a virtual environment
RUN python3 -m venv /app/venv

# Activate the virtual environment and ensure pip is up-to-date
RUN /app/venv/bin/pip install --upgrade pip

# Set the default command to run the Python interpreter in the virtual environment
CMD ["/app/venv/bin/python3"]
