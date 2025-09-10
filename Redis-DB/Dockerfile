# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY pyproject.toml .

# Install any needed packages specified in pyproject.toml
RUN pip install "fastapi>=0.116.1" "uvicorn>=0.23.2" "redis>=5.0.1"

# Copy the rest of the application code to the working directory
COPY . .

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]


