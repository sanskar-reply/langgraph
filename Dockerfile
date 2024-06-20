# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app's source code into the container at /app
COPY . /app

# Expose the port your Chainlit app runs on (default is 8000, change if necessary)
# # EXPOSE 8080
# ENV HOST=0.0.0.0
# ENV LISTEN_PORT 8000
EXPOSE 8000

# Run the Chainlit app (assuming your main app file is sales.py)
CMD ["chainlit", "run", "chainlit-gcp/sales.py"]
