# Use Python as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for API Gateway
EXPOSE 5000

# Run the API Gateway
CMD ["python", "APIGateway.py"]
