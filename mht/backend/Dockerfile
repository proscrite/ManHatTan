# Use an official, lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
# (Assuming your main FastAPI file is inside an 'app' folder)
COPY . .

# Expose the port Uvicorn will run on (Default to 8000)
EXPOSE 8000

# Command to run the application dynamically picking up Cloud Run's port
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"