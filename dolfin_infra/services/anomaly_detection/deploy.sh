#!/bin/bash

# Set variables
PROJECT_ID="sit764-dev"
IMAGE_NAME="dolfin-anomaly-detection"
TAG="latest"

# Authenticate with GCP (uncomment if needed)
gcloud auth login
gcloud auth configure-docker

# Build the Docker image
docker buildx build --no-cache --platform=linux/amd64 -t ${IMAGE_NAME}:${TAG} .

# Tag the image for uploading to Google Container Registry
docker tag ${IMAGE_NAME}:${TAG} gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG}

# Push the image to Google Container Registry
docker push gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG}

# Confirm completion
echo "Docker image pushed to GCR."
