# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for the Flet app
EXPOSE 5000

# Define environment variable for Flet configuration
ENV FLET_SERVER_PORT=5000

# Run the application
CMD ["python", "main.py"]
