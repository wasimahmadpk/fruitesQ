# Monitoring the FruitQ Vision Model on Google Cloud

This guide explains how to monitor your **FruitQ API** (and the CLIP vision model) when it runs on **Google Cloud Run**.

---

## 1. Cloud Run Logs (where to look first)

All output from your app (including model load and errors) goes to **Cloud Logging**.

**Open logs:**
1. Go to **https://console.cloud.google.com/run**
2. Click your service **fruitq-api**
3. Open the **"Logs"** tab (or **"View logs"**).

**What you’ll see:**
- **Model load** — e.g. `Loading model openai/clip-vit-base-patch32`
- **Prediction errors** — e.g. `Model inference failed` with a stack trace
- **HTTP requests** — method, path, status code (200, 500, etc.)
- **Low-confidence alerts** — when MLflow tags a run (if logging is used)

**Filter by severity:**
- In the Logs viewer, use the severity dropdown: **Error**, **Warning**, **Info**.
- To see only errors: set severity to **Error** or search for `"Model inference failed"`.

**Direct link (replace `fruitesq` with your project ID):**  
https://console.cloud.google.com/logs/query?project=fruitesq

Example query for errors from the FruitQ API:
```text
resource.type="cloud_run_revision"
resource.labels.service_name="fruitq-api"
severity>=ERROR
```

---

## 2. Cloud Run Metrics (traffic, latency, errors)

Cloud Run exposes metrics automatically. Use them to see how often the model is called and how it behaves.

**Open metrics:**
1. Go to **https://console.cloud.google.com/run**
2. Click **fruitq-api**
3. Open the **"Metrics"** tab.

**Useful metrics:**

| Metric | What it tells you |
|--------|--------------------|
| **Request count** | How many calls to `/predict` and other endpoints |
| **Request latency** | Response time (e.g. first request slow when model loads, then faster) |
| **Container memory** | RAM use (e.g. spike when the model loads) |
| **Container CPU** | CPU use during inference |
| **Error rate** | % of 5xx (and optionally 4xx) responses |

**Create a dashboard:**
1. In the Cloud Console, go to **Monitoring** → **Dashboards** (or https://console.cloud.google.com/monitoring/dashboards).
2. **Create dashboard** → **Add chart**.
3. Select **Resource type:** Cloud Run Revision, **Metric:** e.g. Request count or Latency, and filter by **Service name:** `fruitq-api`.

---

## 3. Alerts (get notified when something goes wrong)

**Example: alert when the API is failing a lot.**

1. Go to **Monitoring** → **Alerting**: https://console.cloud.google.com/monitoring/alerting
2. **Create policy** → **Add condition**.
3. **Select metric:** e.g. **Cloud Run** → **Request count** (or **Error count** if available).
4. Filter by **Service name** = `fruitq-api`.
5. Optional: use **Error count** or a ratio like **5xx / total requests**.
6. Set a **threshold** (e.g. error rate > 5% or errors > 10 in 5 minutes).
7. **Configure notifications** — e.g. email or Slack.

**Example: alert when latency is very high (e.g. model stuck or overloaded).**

1. Same **Create policy** → **Add condition**.
2. **Metric:** Cloud Run → **Request latency** (e.g. 95th percentile).
3. Filter by **Service name** = `fruitq-api`.
4. **Threshold:** e.g. latency > 120 seconds for 5 minutes.
5. Add notification channel.

---

## 4. What’s logged today (vision model and API)

- **On model load:** `Loading model openai/clip-vit-base-patch32`, `Model loaded.`
- **On prediction failure:** `Model inference failed` plus the exception (e.g. 429, OOM, missing dependency).
- **On low confidence:** MLflow tags the run (only if MLflow is used and the tag is logged; in Cloud Run, MLflow data is in-memory/ephemeral unless you point it to a remote store).

So for **monitoring the vision model** on Google Cloud, use:
- **Logs** for load events, errors, and stack traces.
- **Metrics** for request volume, latency, memory, and CPU.
- **Alerts** for high error rate or very high latency.

---

## 5. MLflow and Cloud Run (optional)

In the current setup, **MLflow writes to a local directory** inside the container. On Cloud Run that storage is **temporary**: when the instance stops, those runs are lost. So you do **not** get a persistent MLflow history of predictions on Cloud Run unless you change the setup.

**If you want to keep prediction history in MLflow on GCP:**
- Run an **MLflow server** (e.g. on Cloud Run or GCE) with a **backend store** and **artifact store** in **Google Cloud Storage (GCS)**.
- Set **MLFLOW_TRACKING_URI** in the FruitQ API container to that server’s URL.
- Then you can use the MLflow UI to monitor runs, compare confidence over time, and drill into low-confidence predictions.

For most people, **Cloud Run logs + metrics + alerts** are enough to monitor the vision model; add MLflow on GCS only if you need long-term experiment and prediction history.
