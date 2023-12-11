read -p "What is the project ID of the Google Cloud project you want to deploy to? [$PROJECT_NAME]" GOOGLE_PROJECT
GOOGLE_PROJECT=${GOOGLE_PROJECT:-$PROJECT_NAME}

gcloud services enable --project="${GOOGLE_PROJECT}" cloudresourcemanager.googleapis.com
gcloud services enable --project="${GOOGLE_PROJECT}" compute.googleapis.com
gcloud services enable --project="${GOOGLE_PROJECT}" servicenetworking.googleapis.com
gcloud services enable --project="${GOOGLE_PROJECT}" sqladmin.googleapis.com
gcloud services enable --project="${GOOGLE_PROJECT}" appengine.googleapis.com

