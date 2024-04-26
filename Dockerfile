FROM ubuntu:latest
LABEL authors="Ben Soones"

FROM python:3.12

# Set the working directory inside the container
WORKDIR /adventure-works-api

# Copy the current directory contents into the container at /app
COPY . /adventure-works-api

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["uvicorn","main:app", "--host","0.0.0.0","--port","3002"]
