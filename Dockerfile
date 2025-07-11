# backend/Dockerfile
# Use a slim Python image for smaller size
FROM python:3.12.9

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port your FastAPI application listens on
EXPOSE 8000

# Command to run the FastAPI application using Uvicorn
# --host 0.0.0.0 is crucial to make it accessible from outside the container
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
