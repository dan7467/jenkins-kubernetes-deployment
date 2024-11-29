# 1. Basic Docker Container (no kubernetes or jenkins config here): ################################################################################
FROM python:3.12-slim

# Set environment variables to prevent Python from buffering and creating pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the project requirements to the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the entire project to the container
COPY . /app/

# Expose the port Flask will run on
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# Command to run the application
CMD ["flask", "run", "--host=0.0.0.0"]

# # 2. Jenkins Container: #####################################################################################################################
# FROM jenkins/jenkins:2.414.3-jdk17
# USER root
# RUN apt-get update && apt-get install -y lsb-release
# RUN curl -fsSLo /usr/share/keyrings/docker-archive-keyring.asc \
# https://download.docker.com/linux/debian/gpg
# RUN echo "deb [arch=$(dpkg --print-architecture) \
# signed-by=/usr/share/keyrings/docker-archive-keyring.asc] \
# https://download.docker.com/linux/debian \
# $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list
# RUN apt-get update && apt-get install -y docker-ce-cli
# USER jenkins
# RUN jenkins-plugin-cli --plugins "blueocean docker-workflow json-path-api"

# # # 3. Kubernetes Jenkins Pipeline: ####################################################################################################################
# #It will use node:19-alpine3.16 as the parent image for 
# #building the Docker image
# FROM node:19-alpine3.16
# #It will create a working directory for Docker. The Docker
# #image will be created in this working directory.
# WORKDIR /jobhaven-app
# #Copy the application's dependencies from here 
# #to the jobhaven-app working directory and install
# COPY requirements.txt .
# RUN pip install --upgrade pip && \
#     pip install -r requirements.txt
# # <!-- Copy the remaining React.js application folders and files from 
# #  the `jenkins-kubernetes-deployment` local folder to the Docker 
# # react-app working directory -->
# COPY . .
# #Expose the React.js application container on port 3000
# EXPOSE 3000
# #The command to start the React.js application container
# CMD ["npm", "start"]