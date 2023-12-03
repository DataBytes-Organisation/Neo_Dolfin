FROM ubuntu:latest

RUN apt-get update -y

RUN apt-get install -y python3-pip python3-dev build-essential

COPY . /app

# Set the working directory in the container
WORKDIR /app

# Install packages listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python3"]

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variables here
#ENV NAME World

# Run app.py when the container launches
CMD ["./app.py"]
