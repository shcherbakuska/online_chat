# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file if you have any additional dependencies (optional)
COPY requirements.txt .

# Install FastAPI and Uvicorn
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8123

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8123"]