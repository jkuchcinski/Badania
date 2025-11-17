#!/bin/bash

# Skrypt do wdrożenia aplikacji na Google Cloud Run
# Project ID: hipokrates-478419

PROJECT_ID="hipokrates-478419"
IMAGE_NAME="gcr.io/${PROJECT_ID}/badania-app"
SERVICE_NAME="badania-app"
REGION="europe-west1"

echo "🔨 Budowanie obrazu Docker..."
gcloud builds submit --tag ${IMAGE_NAME}

echo "🚀 Wdrażanie na Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --port 8080

echo "✅ Wdrożenie zakończone!"
echo "🌐 Sprawdź URL aplikacji powyżej"

