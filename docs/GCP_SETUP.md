# Deploy FruitQ to Google Cloud (Step-by-Step)

This guide walks you through creating a Google Cloud account and deploying FruitQ to **Cloud Run** via GitHub Actions.

---

## 1. Create a Google Cloud account

1. Go to **[https://cloud.google.com/free](https://cloud.google.com/free)**.
2. Click **"Get started for free"**.
3. Sign in with a Google account (or create one).
4. Enter your country and accept the terms.
5. Add a payment method (card). You get **$300 free credits for 90 days** and are not charged unless you turn on billing and exceed free tier.
6. Complete signup. You will land in the [Cloud Console](https://console.cloud.google.com).

---

## 2. Create a project

1. In the Cloud Console, open the project dropdown at the top (next to "Google Cloud").
2. Click **"New Project"**.
3. Name it (e.g. `fruitq-app`). Note the **Project ID** (e.g. `fruitq-app-12345`). You will need it later.
4. Click **Create**.

---

## 3. Enable billing (required for Cloud Run)

1. Go to **Billing** in the left menu (or [console.cloud.google.com/billing](https://console.cloud.google.com/billing)).
2. Link a billing account to your project (the $300 free credits apply here).
3. Cloud Run and Artifact Registry will use this; you stay within free tier for light use.

---

## 3b. Create GCS bucket for Terraform state (one-time)

So Terraform can update existing Cloud Run services (instead of failing with "already exists"), state is stored in a GCS bucket.

1. Open **[Cloud Storage](https://console.cloud.google.com/storage/browser)** in your project.
2. Click **CREATE BUCKET**.
3. **Name:** `YOUR_PROJECT_ID-fruitq-tfstate` (e.g. if Project ID is `myapp-123`, use `myapp-123-fruitq-tfstate`).
4. **Location type:** Region → same as your `GCP_REGION` (e.g. `us-central1`).
5. Click **CREATE**.

If you skip this, the workflow will try to create the bucket; if the service account lacks permission, create the bucket manually as above.

---

## 3c. Enable required APIs (one-time)

The deploy needs **Artifact Registry** and **Cloud Run** to be enabled in your project:

1. [Enable Artifact Registry](https://console.cloud.google.com/apis/library/artifactregistry.googleapis.com) — select your project → **ENABLE**.
2. [Enable Cloud Run](https://console.cloud.google.com/apis/library/run.googleapis.com) — select your project → **ENABLE**.
3. Wait 1–2 minutes before the first deploy.

---

## 4. Create a service account for GitHub Actions

**This step is done in Google Cloud (not GitHub).** A **service account** is like a robot user. GitHub Actions will use it to deploy your app to Google Cloud. You create it in the Google Cloud Console and then paste the key into GitHub as a secret.

### Step 4.1 — Open Service Accounts (in Google Cloud)

1. In your browser, go to: **[https://console.cloud.google.com/iam-admin/serviceaccounts](https://console.cloud.google.com/iam-admin/serviceaccounts)**
2. At the top, make sure the **correct project** is selected (the one you created in step 2). If not, click the project name and choose your project (e.g. `fruitq-app`).
3. Click the blue **"+ CREATE SERVICE ACCOUNT"** button at the top.

### Step 4.2 — Name the service account

1. **Service account name:** type `github-actions-fruitq` (or any name you like).
2. **Service account ID** will fill in automatically.
3. Click **"CREATE AND CONTINUE"** at the bottom.

### Step 4.3 — Give it the right roles

You need to add three roles so it can deploy to Cloud Run and push images.

1. Click the **"Role"** dropdown.
2. In the search box, type **Cloud Run Admin**. Select **"Cloud Run Admin"** from the list. Click **"ADD ANOTHER ROLE"**.
3. In the second Role dropdown, search for **Artifact Registry Administrator**. Select it. Click **"ADD ANOTHER ROLE"** again.
4. In the third Role dropdown, search for **Service Account User**. Select it.
5. Click **"CONTINUE"** at the bottom.
6. On the next screen (optional), click **"DONE"**.

### Step 4.4 — Create and download the key (JSON)

1. You should now see a list of service accounts. Find **github-actions-fruitq** (or the name you used) and **click on its email** (e.g. `github-actions-fruitq@your-project.iam.gserviceaccount.com`).
2. Open the **"KEYS"** tab at the top.
3. Click **"ADD KEY"** → **"Create new key"**.
4. Choose **"JSON"** and click **"CREATE"**. A JSON file will download to your computer (e.g. `your-project-abc123.json`).
5. **Keep this file safe and private.** You will copy its contents into GitHub in the next section. Do not share the file or commit it to Git.

---

## 5. Add the three secrets to GitHub

GitHub Actions needs three pieces of information to deploy to Google Cloud. You add them as **repository secrets** so they are stored securely and never shown in logs.

### Step 5.1 — Open your repo’s secret settings

1. Go to your FruitQ repo: **https://github.com/wasimahmadpk/fruitesQ**
2. Click the **"Settings"** tab (top menu of the repo; not your profile settings).
3. In the left sidebar, under **"Security"**, click **"Secrets and variables"** → **"Actions"**.
4. You will see **"Repository secrets"**. This is where you add the three secrets.

### Step 5.2 — Add the first secret: `GCP_PROJECT_ID`

1. Click **"New repository secret"**.
2. **Name:** type exactly: `GCP_PROJECT_ID` (all caps, with underscores).
3. **Secret:** type your **Google Cloud Project ID** (e.g. `fruitq-app-12345`). You can find it in the Google Cloud Console at the top when your project is selected, or in the project list. It is usually the project name in lowercase with numbers.
4. Click **"Add secret"**.

### Step 5.3 — Add the second secret: `GCP_REGION`

1. Click **"New repository secret"** again.
2. **Name:** type exactly: `GCP_REGION`.
3. **Secret:** type: `us-central1` (this is a Google Cloud region; you can use another like `europe-west1` if you prefer).
4. Click **"Add secret"**.

### Step 5.4 — Add the third secret: `GCP_SA_KEY`

1. Open the **JSON key file** you downloaded in step 4.4 (e.g. with Notepad, TextEdit, or VS Code). You will see something like:
   ```json
   {
     "type": "service_account",
     "project_id": "your-project-123",
     "private_key_id": "...",
     "private_key": "-----BEGIN PRIVATE KEY-----\n...",
     ...
   }
   ```
2. Select **all** the text in the file (Ctrl+A or Cmd+A) and **copy** it (Ctrl+C or Cmd+C).
3. In GitHub, click **"New repository secret"** again.
4. **Name:** type exactly: `GCP_SA_KEY`.
5. **Secret:** **paste** the entire JSON (the whole file content) into the box. Do not change or remove any character; it must be one valid JSON object.
6. Click **"Add secret"**.

### Step 5.5 — Check that all three are there

Under **"Repository secrets"** you should see:

| Name            | Updated    |
|-----------------|------------|
| `GCP_PROJECT_ID`| Just now   |
| `GCP_REGION`    | Just now   |
| `GCP_SA_KEY`    | Just now   |

(You will not see the secret values, only the names — that’s normal.)

---

## 6. Deploy

1. Ensure your Docker image is built and pushed to GHCR on the `main` branch (the existing **Build & Push** job does this).
2. Push a commit to `main` (or merge a PR). The **Deploy to GCP (Cloud Run)** job will:
   - Create Artifact Registry and push the image from GHCR to GCP
   - Run Terraform to create two Cloud Run services (API + Dashboard)
3. Check **Actions** tab for the workflow run. When it succeeds, Terraform outputs the URLs in the job log (or run `terraform output` in `terraform-gcp/` after a local apply).

---

## 7. Run Terraform locally (optional)

If you prefer to deploy from your machine instead of CI:

```bash
# Install gcloud CLI: https://cloud.google.com/sdk/docs/install
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID

cd terraform-gcp
terraform init
terraform apply -var="project_id=YOUR_PROJECT_ID" -var="region=us-central1"
```

The image must exist in Artifact Registry first. Either run the GitHub Actions workflow once to push it, or build and push manually:

```bash
docker build -t fruitq .
docker tag fruitq us-central1-docker.pkg.dev/YOUR_PROJECT_ID/fruitq/api:latest
gcloud auth configure-docker us-central1-docker.pkg.dev
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/fruitq/api:latest
terraform apply -var="project_id=YOUR_PROJECT_ID" -var="region=us-central1"
```

---

## Summary

- **Account**: [cloud.google.com/free](https://cloud.google.com/free) → $300 credits, 90 days.
- **Secrets**: `GCP_PROJECT_ID`, `GCP_REGION`, `GCP_SA_KEY` in GitHub repo settings.
- **Deploy**: Push to `main` → GitHub Actions builds, pushes to GCP, runs Terraform → Cloud Run URLs in the workflow log.

---

## Troubleshooting

### "Resource 'fruitq-api' already exists" (Terraform 409)

Terraform state was not persisted, so it tried to create a service that already exists. Fix:

1. Create the **GCS bucket for Terraform state** (see step **3b** above) if you haven’t.
2. Re-run the workflow. The job will use the bucket for state, so the next run will **update** the existing services instead of creating them.

### "Repository \"fruitq\" not found" (push fails)

The Artifact Registry repo must exist before the workflow can push. Create it once:

1. Open **[Artifact Registry](https://console.cloud.google.com/artifacts)** in Google Cloud Console.
2. Select your **project** at the top.
3. Click **"+ CREATE REPOSITORY"**.
4. **Name:** `fruitq` (must be exactly this).
5. **Format:** **Docker**.
6. **Mode:** Standard.
7. **Location type:** **Region** → choose the **same region** as your `GCP_REGION` secret (e.g. **us-central1**).
8. Click **"CREATE"**.
9. In GitHub: **Actions** → open the failed run → **"Re-run all jobs"**.

After that, the push step should succeed.

### "Artifact Registry API has not been used in project ... or it is disabled"

Enable the API once in your project:

1. Open: **[https://console.cloud.google.com/apis/library/artifactregistry.googleapis.com](https://console.cloud.google.com/apis/library/artifactregistry.googleapis.com)**
2. Select your **project** at the top.
3. Click **"ENABLE"**.
4. Also enable **Cloud Run** if needed: [https://console.cloud.google.com/apis/library/run.googleapis.com](https://console.cloud.google.com/apis/library/run.googleapis.com) → **ENABLE**.
5. Wait 1–2 minutes, then re-run the failed workflow: **Actions** → open the run → **Re-run all jobs**.
