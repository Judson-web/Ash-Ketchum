# Nexus Deployment Guide (Google Cloud Run)

## 1) Prerequisites
- Google Cloud project with billing enabled.
- `gcloud` CLI installed and authenticated.
- Gemini API key.
- Firebase project + service account JSON (optional but recommended for persistent chat history).

## 2) Enable services
```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```

## 3) Build and deploy
```bash
PROJECT_ID="your-project-id"
REGION="us-central1"
SERVICE="nexus"

gcloud builds submit --tag "gcr.io/${PROJECT_ID}/${SERVICE}"

gcloud run deploy "${SERVICE}" \
  --image "gcr.io/${PROJECT_ID}/${SERVICE}" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars "ENV=production,GEMINI_API_KEY=YOUR_KEY,FIREBASE_PROJECT_ID=${PROJECT_ID}" \
  --set-secrets "FIREBASE_CREDENTIALS_JSON=firebase-service-account:latest"
```

> If you don't use Secret Manager, you can pass `FIREBASE_CREDENTIALS_JSON` as an env var directly (less secure).

## 4) Post-deploy checks
- Open `/api/health` and verify:
  - `gemini: google-genai`
  - `firebase: firestore` (or `disabled` if intentionally off)

## 5) Production recommendations
- Restrict CORS to your domain.
- Add Cloud Armor / IAP if needed.
- Add rate limits and bot-abuse mitigation.
- Wire Cloud Logging alerts for exceptions.
