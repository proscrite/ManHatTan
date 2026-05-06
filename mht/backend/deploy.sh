#!/bin/bash

# Exit immediately if any command fails
set -e

echo "🚀 Starting deployment of Manhattan API to Google Cloud Run..."

# --- Configuration ---
PROJECT_ID="manhattan-lang"
REGION="europe-southwest1"
REPO_NAME="manhattan-repo"
IMAGE_NAME="manhattan_api"
TAG="v1" # You can change this to "v2", "v3", or `$(date +%s)` for unique versions
SERVICE_NAME="manhattan-api"

IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${TAG}"

echo "📦 1/4: Building the Docker image (Cross-platform for Google servers: linux/amd64)..."
docker build --platform linux/amd64 -t ${IMAGE_NAME}:latest .

echo "🏷️ 2/4: Tagging the image for Artifact Registry..."
docker tag ${IMAGE_NAME}:latest ${IMAGE_URL}

echo "☁️ 3/4: Pushing image to Google Cloud Artifact Registry..."
docker push ${IMAGE_URL}

echo "🚀 4/4: Deploying to Cloud Run..."
# Note: We do NOT need to include --set-env-vars here! 
# Cloud Run automatically remembers the environment variables from your previous deployment.
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_URL} \
  --region ${REGION} \
  --allow-unauthenticated

echo "✅ Deployment complete! Your API is live."
