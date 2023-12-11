
#!/bin/bash

# Set variables
PROJECT_ID="sit764-dev"

# Authenticate with GCP (uncomment if needed)
#gcloud auth login

# Build the Docker image
source services/anomaly_detection/build_image.sh $PROJECT_ID

# Deploy the Terraform Infrastructure
terraform apply -auto-approve -var credentials_file=~/path_to_your_creds.json -lock=false
