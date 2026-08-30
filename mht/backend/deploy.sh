#!/bin/bash

# Exit immediately if any command fails
set -e

echo "🔑 Loading environment variables from .env..."
if [ -f .env ]; then
  # Enable automatic exporting of variables
  set -o allexport
  source .env
  set +o allexport
else
  echo "⚠️ Warning: .env file not found."
fi

echo "🚀 Starting deployment of Manhattan API to Google Cloud Run..."

# --- Configuration ---
PROJECT_ID="manhattan-lang"
REGION="europe-southwest1"
REPO_NAME="manhattan-repo"
IMAGE_NAME="manhattan_api"

GEMINI_API_KEY="${GEMINI_API_KEY}"
GROQ_API_KEY="${GROQ_API_KEY}"
OPENROUTER_API_KEY="${OPENROUTER_API_KEY}"

SECRET_KEY="${SECRET_KEY}"
DATABASE_URL="${DATABASE_URL}"

TAG=$(git rev-parse --short HEAD)
SERVICE_NAME="manhattan-api"

IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${TAG}"

echo "📦 1/4: Building the Docker image (Cross-platform for Google servers: linux/amd64)..."
docker build --platform linux/amd64 -t ${IMAGE_NAME}:latest .

echo "🏷️ 2/4: Tagging the image for Artifact Registry..."
docker tag ${IMAGE_NAME}:latest ${IMAGE_URL}

echo "☁️ 3/4: Pushing image to Google Cloud Artifact Registry..."
docker push ${IMAGE_URL}

# Extract Zilliz credentials from your .env
ZILLIZ_CLUSTER_URL="${ZILLIZ_CLUSTER_URL}"
ZILLIZ_API_KEY="${ZILLIZ_API_KEY}"

echo "🚀 4/4: Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_URL} \
  --region ${REGION} \
  --set-env-vars="GEMINI_API_KEY=${GEMINI_API_KEY},GROQ_API_KEY=${GROQ_API_KEY},OPENROUTER_API_KEY=${OPENROUTER_API_KEY}" \
  --set-env-vars="DATABASE_URL=${DATABASE_URL},SECRET_KEY=${SECRET_KEY}" \
  --set-env-vars="ZILLIZ_CLUSTER_URL=${ZILLIZ_CLUSTER_URL},ZILLIZ_API_KEY=${ZILLIZ_API_KEY}" \
  --allow-unauthenticated

echo "✅ Deployment complete! Your API is live."
