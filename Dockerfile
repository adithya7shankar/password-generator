# Use an official Python runtime as a parent image
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for the Flet app (if using web version)
EXPOSE 5000

# Define environment variable (if needed for Flet configuration)
ENV FLET_SERVER_PORT=5000

# Run the Flet app
CMD ["python", "mainfn.py"]
