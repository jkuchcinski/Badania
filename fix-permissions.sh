#!/bin/bash

# Skrypt do naprawy uprawnień Cloud Build
# Project ID: hipokrates-478419

PROJECT_ID="hipokrates-478419"
PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")

echo "🔧 Naprawianie uprawnień dla Cloud Build..."
echo "Project ID: ${PROJECT_ID}"
echo "Project Number: ${PROJECT_NUMBER}"

# Pobierz email konta serwisowego Cloud Build
CLOUD_BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

echo "📧 Konto serwisowe Cloud Build: ${CLOUD_BUILD_SA}"

# Nadaj uprawnienia Storage Admin (potrzebne do Container Registry)
echo "🔐 Nadawanie uprawnień Storage Admin..."
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${CLOUD_BUILD_SA}" \
  --role="roles/storage.admin"

# Nadaj uprawnienia Service Account User (potrzebne do Cloud Run)
echo "🔐 Nadawanie uprawnień Service Account User..."
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${CLOUD_BUILD_SA}" \
  --role="roles/iam.serviceAccountUser"

# Nadaj uprawnienia Cloud Run Admin (potrzebne do wdrożenia)
echo "🔐 Nadawanie uprawnień Cloud Run Admin..."
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${CLOUD_BUILD_SA}" \
  --role="roles/run.admin"

echo "✅ Uprawnienia zostały nadane!"
echo "🔄 Teraz możesz spróbować ponownie:"
echo "   ./deploy.sh"
echo "   lub"
echo "   gcloud builds submit --config cloudbuild.yaml"

