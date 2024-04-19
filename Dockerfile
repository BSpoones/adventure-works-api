FROM ubuntu:latest
LABEL authors="BSpoones"

FROM python:3.12

# Set the working directory inside the container
WORKDIR /adventure-works-api

# Copy the current directory contents into the container at /app
COPY . /adventure-works-api

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["uvicorn","main:app"]
