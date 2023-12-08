FROM python:3.9-slim

RUN apt-get update  -y

# Set the working directory in the container
WORKDIR /app
COPY . /app

# Install packages listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variables here
#ENV NAME World

# Run app.py when the container launches
CMD ["python", "./app.py"]
