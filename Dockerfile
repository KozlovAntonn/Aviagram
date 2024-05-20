# Use an official Python runtime as a parent image
# FROM python:3.9
FROM --platform=linux/amd64 python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

# Install locales
RUN apt-get clean && apt-get update && apt-get install -y locales
RUN locale-gen ru_RU.UTF-8

ENV LANG ru_RU.UTF-8  
ENV LANGUAGE ru_RU:ru  
ENV LC_ALL ru_RU.UTF-8

# Copy the rest of the application code into the container at /app
COPY . .

# Define the command to run your application
CMD ["python", "a1_main.py"]

EXPOSE 5000