#!/bin/bash

# Skrypt do wdrożenia aplikacji na Google Cloud Run
# Project ID: hipokrates-478419

PROJECT_ID="hipokrates-478419"
IMAGE_NAME="gcr.io/${PROJECT_ID}/badania-app"
SERVICE_NAME="badania-app"
REGION="europe-west1"

echo "🔧 Przełączanie na projekt Google Cloud..."
gcloud config set project ${PROJECT_ID}

echo "🔨 Budowanie obrazu Docker (platform: linux/amd64)..."
gcloud builds submit --tag ${IMAGE_NAME} --platform linux/amd64

echo "🚀 Wdrażanie na Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars ADMIN_PASSWORD=hipokrates,SECRET_KEY=GZ55q2jtgI3m6NL1hMd_HqlFGnTxNyxY8XJZzKy2e04

echo "✅ Wdrożenie zakończone!"
echo "🌐 Sprawdź URL aplikacji powyżej"

