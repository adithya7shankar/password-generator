FROM ubuntu:22.04


# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    python3-setuptools \
    python3-venv \
    python3-wheel \
    && apt-get clean

# Set the working directory

WORKDIR /app

RUN python3 -m venv /app/venv

# Activate the virtual environment
ENV PATH="/app/venv/bin:$PATH"

# Copy the current directory contents into the container at /app

COPY . /app

RUN pip install --upgrade pip

# Make port 8000 available to the world outside this container

EXPOSE 8000

# Define environment variable

# Run app.py when the container launches

CMD ["generator-for-me"]
