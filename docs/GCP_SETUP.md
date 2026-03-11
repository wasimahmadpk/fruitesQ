# FruitQ — Google Cloud Deployment Guide

This guide explains how to deploy FruitQ to the cloud using **Google Cloud Run**. Follow each step in order. No prior cloud experience needed.

---

## What you will set up

| Step | What you do |
|---|---|
| 1 | Create a free Google Cloud account |
| 2 | Create a project |
| 3 | Enable billing |
| 4 | Create a storage bucket (saves deployment state) |
| 5 | Grant the bucket access |
| 6 | Enable the required APIs |
| 7 | Create a service account (a robot user for GitHub) |
| 8 | Download the JSON key |
| 9 | Add secrets to GitHub |
| 10 | Deploy |

---

## Step 1 — Create a Google Cloud account

1. Open: **https://cloud.google.com/free**
2. Click **"Get started for free"**.
3. Sign in with your Google account (Gmail). If you don't have one, create one — it's free.
4. Accept the terms and choose your country.
5. Add a **credit or debit card** (Google uses it only to verify your identity).
   - You will **NOT** be charged automatically.
   - You receive **$300 in free credits for 90 days**.
6. Click **Start my free trial**. You will land in the **Google Cloud Console**.

> The Cloud Console is at: **https://console.cloud.google.com**

---

## Step 2 — Create a project

A project is like a folder that holds all your cloud resources.

1. In the Console, click the **project dropdown** at the top (next to the Google Cloud logo).
2. Click **"New Project"**.
3. Give it a name (e.g. `fruitq-app`).
4. Look at the **Project ID** (shown below the name, e.g. `fruitq-app-12345`). **Copy it** — you will need it later.
5. Click **Create**.

> The **Project ID** is what you use in settings and commands. It's NOT the same as the project name.

---

## Step 3 — Enable billing

Cloud Run requires billing to be enabled (your free credits cover this).

1. In the Console, open the left menu and click **"Billing"** (or go to https://console.cloud.google.com/billing).
2. Click **"Link a billing account"** and follow the prompts.
3. Your $300 free credits will apply automatically.

---

## Step 4 — Create a storage bucket for Terraform state

Terraform (the tool that deploys your Cloud Run services) needs somewhere to save its progress. This prevents errors when you deploy multiple times.

1. Open **Cloud Storage**: https://console.cloud.google.com/storage/browser
2. Make sure your project is selected at the top.
3. Click **"Create bucket"** (or **"+ Create"**).
4. **Bucket name:** type your Project ID, then `-fruitq-tfstate`.
   - Example: if your Project ID is `fruitq-app-12345`, the bucket name is `fruitq-app-12345-fruitq-tfstate`.
   - Bucket names must be globally unique — this format ensures that.
5. **Location type:** choose **"Region"**.
6. **Region:** choose `us-central1` (or the same region you'll use throughout).
7. Click **"Create"**.

---

## Step 5 — Create a service account

A service account is like a robot user. GitHub Actions will use it to deploy to Google Cloud on your behalf.

### 5a — Open service accounts

1. Open: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Make sure your project is selected at the top.
3. Click **"+ Create service account"**.

### 5b — Name it

1. **Service account name:** type `github-actions-fruitq`.
2. The **Service account ID** will fill automatically (e.g. `github-actions-fruitq@fruitq-app-12345.iam.gserviceaccount.com`). **Copy this email** — you need it in step 6.
3. Click **"Create and continue"**.

### 5c — Assign roles

Roles tell Google what this account is allowed to do. Add these three:

1. Click the **"Role"** dropdown.
2. Search for **Cloud Run Admin** → select it → click **"Add another role"**.
3. Search for **Artifact Registry Administrator** → select it → click **"Add another role"**.
4. Search for **Service Account User** → select it.
5. Click **"Continue"** → **"Done"**.

### 5d — Download the JSON key

1. In the service accounts list, click on the email of the account you just created.
2. Click the **"Keys"** tab.
3. Click **"Add key"** → **"Create new key"**.
4. Choose **JSON** → click **"Create"**.
5. A `.json` file downloads to your computer. **Keep this file safe and do not share it.**

---

## Step 6 — Grant the bucket access to the service account

The service account needs permission to read and write to the Terraform state bucket.

1. Go back to **Cloud Storage**: https://console.cloud.google.com/storage/browser
2. Click the bucket you created in step 4 (e.g. `fruitq-app-12345-fruitq-tfstate`).
3. Click the **"Permissions"** tab.
4. Click **"Grant access"**.
5. **New principals:** paste the service account email from step 5b.
6. **Role:** choose **Storage Admin**.
7. Click **"Save"**.

---

## Step 7 — Enable the required APIs

Two services need to be activated in your project. This is a one-time step.

1. Enable **Artifact Registry** (stores your Docker image):
   - Open: https://console.cloud.google.com/apis/library/artifactregistry.googleapis.com
   - Select your project → click **"Enable"**.

2. Enable **Cloud Run** (runs your app):
   - Open: https://console.cloud.google.com/apis/library/run.googleapis.com
   - Select your project → click **"Enable"**.

3. Wait 1–2 minutes for the changes to take effect.

---

## Step 8 — Create the Artifact Registry repository

This is where your Docker image will be stored on Google Cloud.

1. Open: https://console.cloud.google.com/artifacts
2. Select your project at the top.
3. Click **"+ Create repository"**.
4. Fill in:
   - **Name:** `fruitq` (must be exactly this).
   - **Format:** Docker.
   - **Location type:** Region.
   - **Region:** `us-central1` (same as your bucket).
5. Click **"Create"**.

---

## Step 9 — Add secrets to GitHub

GitHub Actions needs to know your GCP credentials to deploy. You store them as secrets in your GitHub repo — they are never visible in logs.

1. Open your repo: **https://github.com/wasimahmadpk/fruitesQ**
2. Go to **Settings** → **Secrets and variables** → **Actions**.
3. Click **"New repository secret"** for each of the following:

| Secret name | What to paste |
|---|---|
| `GCP_PROJECT_ID` | Your GCP Project ID (e.g. `fruitq-app-12345`) |
| `GCP_REGION` | `us-central1` |
| `GCP_SA_KEY` | The **entire contents** of the JSON key file from step 5d (open the file, select all, copy, paste) |
| `HF_TOKEN` | A Hugging Face read token — creates one free at https://huggingface.co/settings/tokens — prevents 429 errors when loading the AI model |

> After adding all four secrets, you should see `GCP_PROJECT_ID`, `GCP_REGION`, `GCP_SA_KEY`, and `HF_TOKEN` in the secrets list.

---

## Step 10 — Deploy

Push any commit to the `main` branch of your GitHub repository. This automatically triggers the full pipeline:

1. **Tests** run (`pytest`).
2. **Docker image** is built and pushed to GitHub Container Registry.
3. Image is pushed to **Google Artifact Registry**.
4. **Terraform** deploys the API and Dashboard to **Cloud Run**.

**To monitor the deploy:**
1. Open: **https://github.com/wasimahmadpk/fruitesQ/actions**
2. Click the latest run.
3. Wait for all jobs to show a green tick.
4. Open the **"Deploy to GCP (Cloud Run)"** job.
5. Scroll to the bottom of the log — Terraform prints your live URLs:
   - `api_url` — your REST API
   - `dashboard_url` — your Streamlit dashboard

---

## Summary checklist

- [ ] Google Cloud account created
- [ ] Project created; Project ID copied
- [ ] Billing enabled
- [ ] Storage bucket created (`YOUR_PROJECT_ID-fruitq-tfstate`)
- [ ] Bucket access granted to service account (Storage Admin)
- [ ] Artifact Registry API enabled
- [ ] Cloud Run API enabled
- [ ] Artifact Registry repository `fruitq` created
- [ ] Service account `github-actions-fruitq` created with 3 roles
- [ ] JSON key downloaded
- [ ] GitHub secrets added: `GCP_PROJECT_ID`, `GCP_REGION`, `GCP_SA_KEY`, `HF_TOKEN`
- [ ] Push to `main` triggered the deploy → green tick in Actions → live URLs in log

---

## Troubleshooting

### 429 Too Many Requests (Hugging Face rate limit)

The AI model download was blocked because no token was provided. Make sure you added `HF_TOKEN` to GitHub secrets (step 9) and re-run the deploy.

### 500 Internal Server Error on /predict

Check the API logs in Cloud Run:
1. Open https://console.cloud.google.com/run
2. Click **fruitq-api** → **Logs**.
3. Trigger a prediction and read the error message.

Common causes: not enough memory, or the model cache path is wrong (should be `/tmp/hf_cache`).

### "Repository fruitq not found"

You haven't created the Artifact Registry repository yet. Follow step 8 above, then re-run the workflow from GitHub Actions → latest run → Re-run all jobs.

### "Resource fruitq-api already exists" (Terraform 409)

Terraform tried to create a Cloud Run service that already exists, because state was lost. The CI pipeline imports existing services before applying, so re-running the workflow should fix this. If not, check that the state bucket was created correctly and the service account has Storage Admin access.

### "Error acquiring the state lock"

A previous deploy left a lock file in the state bucket. The CI runs with `-lock=false` to avoid this. If you still see it, just re-run the workflow — the lock should clear on its own.

### "Permission denied" on any step

Check that the service account has the correct roles (Cloud Run Admin, Artifact Registry Administrator, Service Account User) and that the service account has Storage Admin on the state bucket.
