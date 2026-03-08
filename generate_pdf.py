"""Generate a professional PDF document for the FruitQ project."""

from fpdf import FPDF
import os

class FruitQPDF(FPDF):
    BLUE = (41, 98, 255)
    DARK = (30, 30, 30)
    GRAY = (100, 100, 100)
    LIGHT_BG = (245, 247, 250)
    WHITE = (255, 255, 255)
    GREEN = (34, 197, 94)
    ORANGE = (249, 115, 22)
    RED = (239, 68, 68)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(*self.GRAY)
            self.cell(0, 10, "FruitQ - AI-Powered Fruit Ripeness Detection System", align="L")
            self.cell(0, 10, f"Page {self.page_no()}", align="R")
            self.ln(12)
            self.set_draw_color(*self.BLUE)
            self.set_line_width(0.3)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*self.GRAY)
        self.cell(0, 10, "github.com/wasimahmadpk/fruitesQ", align="C")

    def section_title(self, num, title):
        self.ln(6)
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(*self.BLUE)
        self.cell(0, 10, f"{num}. {title}", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*self.BLUE)
        self.set_line_width(0.6)
        self.line(10, self.get_y(), 80, self.get_y())
        self.ln(4)

    def sub_title(self, title):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*self.DARK)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*self.DARK)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet(self, text, indent=15):
        x = self.get_x()
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*self.DARK)
        self.set_x(indent)
        self.cell(5, 5.5, "-")
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def code_block(self, text):
        self.set_fill_color(*self.LIGHT_BG)
        self.set_font("Courier", "", 9)
        self.set_text_color(50, 50, 50)
        x = self.get_x()
        self.set_x(15)
        lines = text.strip().split("\n")
        block_height = len(lines) * 5 + 4
        self.rect(15, self.get_y(), 180, block_height, "F")
        self.ln(2)
        for line in lines:
            self.set_x(18)
            self.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")
        self.ln(4)
        self.set_text_color(*self.DARK)

    def table_row(self, cols, widths, bold=False, fill=False):
        style = "B" if bold else ""
        if fill:
            self.set_fill_color(230, 235, 245)
        self.set_font("Helvetica", style, 9)
        self.set_text_color(*self.DARK)
        h = 7
        for i, (col, w) in enumerate(zip(cols, widths)):
            self.cell(w, h, str(col), border=1, fill=fill)
        self.ln(h)


def build_pdf():
    pdf = FruitQPDF()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ── COVER PAGE ─────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.ln(50)
    pdf.set_font("Helvetica", "B", 36)
    pdf.set_text_color(*FruitQPDF.BLUE)
    pdf.cell(0, 15, "FruitQ", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(*FruitQPDF.GRAY)
    pdf.cell(0, 10, "AI-Powered Fruit Ripeness Detection System", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(10)
    pdf.set_draw_color(*FruitQPDF.BLUE)
    pdf.set_line_width(1)
    pdf.line(70, pdf.get_y(), 140, pdf.get_y())
    pdf.ln(10)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*FruitQPDF.DARK)
    pdf.cell(0, 8, "Upload a photo of a fruit -> AI detects ripeness -> Most ripe ships first", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(20)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*FruitQPDF.GRAY)
    pdf.cell(0, 7, "Author: Wasim Ahmad", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Repository: github.com/wasimahmadpk/fruitesQ", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Date: March 2026", align="C", new_x="LMARGIN", new_y="NEXT")

    # ── TABLE OF CONTENTS ──────────────────────────────────────────────────
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*FruitQPDF.BLUE)
    pdf.cell(0, 12, "Table of Contents", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    toc = [
        ("1", "Project Overview"),
        ("2", "Tech Stack"),
        ("3", "Architecture"),
        ("4", "Vision Model - Fruit Identification & Ripeness Detection"),
        ("5", "Ripeness Ranking & Inventory Management"),
        ("6", "REST API (FastAPI)"),
        ("7", "Dashboard UI (Streamlit)"),
        ("8", "MLflow Experiment Tracking"),
        ("9", "Containerization (Docker)"),
        ("10", "CI/CD Pipeline (GitHub Actions)"),
        ("11", "Cloud Deployment (Terraform + Azure)"),
        ("12", "How to Run"),
        ("13", "Project Structure"),
    ]
    for num, title in toc:
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(*FruitQPDF.DARK)
        pdf.cell(10, 7, num + ".")
        pdf.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")

    # ── 1. PROJECT OVERVIEW ────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("1", "Project Overview")
    pdf.body_text(
        "FruitQ is an end-to-end AI system that detects the ripeness of fruits from photos "
        "and automatically prioritises them for shipping. The goal is to reduce food waste by "
        "ensuring the most ripe fruits ship first before they spoil."
    )
    pdf.sub_title("How It Works")
    pdf.bullet("A user uploads a photo of a fruit via the dashboard or API")
    pdf.bullet("A CLIP vision model identifies the fruit type (e.g. banana, mango, apple)")
    pdf.bullet("The same model classifies ripeness into one of four categories")
    pdf.bullet("The fruit is added to an inventory ranked by urgency")
    pdf.bullet("The most ripe fruits are flagged for immediate shipping")

    pdf.ln(3)
    pdf.sub_title("Ripeness Categories & Shipping Priority")
    widths = [50, 50, 50]
    pdf.table_row(["Label", "Priority", "Action"], widths, bold=True, fill=True)
    pdf.table_row(["Overripe", "Today", "Ship immediately"], widths)
    pdf.table_row(["Ripe", "Tomorrow", "Ship next day"], widths)
    pdf.table_row(["Nearly Ripe", "In 3 days", "Monitor"], widths)
    pdf.table_row(["Unripe", "Not yet", "Keep in storage"], widths)

    # ── 2. TECH STACK ──────────────────────────────────────────────────────
    pdf.section_title("2", "Tech Stack")
    widths2 = [50, 60, 80]
    pdf.table_row(["Layer", "Technology", "Purpose"], widths2, bold=True, fill=True)
    pdf.table_row(["Language", "Python 3.11", "Main language"], widths2)
    pdf.table_row(["Vision Model", "CLIP (Hugging Face)", "Fruit ID + ripeness classification"], widths2)
    pdf.table_row(["REST API", "FastAPI + Uvicorn", "Backend endpoints"], widths2)
    pdf.table_row(["Dashboard", "Streamlit + Plotly", "Interactive web UI"], widths2)
    pdf.table_row(["Tracking", "MLflow", "Experiment & prediction logging"], widths2)
    pdf.table_row(["Container", "Docker", "Packaging & portability"], widths2)
    pdf.table_row(["CI/CD", "GitHub Actions", "Automated test, build, deploy"], widths2)
    pdf.table_row(["Cloud IaC", "Terraform", "Azure infrastructure as code"], widths2)
    pdf.table_row(["Cloud", "Azure Container Inst.", "Production hosting"], widths2)

    pdf.ln(3)
    pdf.body_text("Total cost: $0 - all tools are free or have a free tier.")

    # ── 3. ARCHITECTURE ────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("3", "Architecture")
    pdf.body_text(
        "The system follows a clean separation between the AI model, the API layer, "
        "the inventory logic, and the presentation layer. Each component can be developed, "
        "tested, and scaled independently."
    )
    pdf.ln(2)
    pdf.code_block(
        "User (Browser)\n"
        "    |\n"
        "    v\n"
        "Streamlit Dashboard (port 8501)\n"
        "    |  POST /predict (image upload)\n"
        "    |  GET  /inventory\n"
        "    v\n"
        "FastAPI Server (port 8000)\n"
        "    |-- model.py -----> CLIP Model (Hugging Face)\n"
        "    |-- inventory.py -> In-memory ranked inventory\n"
        "    |-- mlflow_tracking -> MLflow (./mlruns)\n"
        "    |\n"
        "Docker Container --> Azure Container Instances\n"
        "    |\n"
        "GitHub Actions CI/CD --> GHCR (image registry)"
    )

    pdf.sub_title("Data Flow")
    pdf.bullet("Image uploaded via Streamlit sidebar or direct API call")
    pdf.bullet("FastAPI receives the image, passes it to the CLIP model")
    pdf.bullet("Model runs two zero-shot classification passes:")
    pdf.bullet("  1) Fruit identification (25 fruit types)", indent=25)
    pdf.bullet("  2) Ripeness classification (4 levels)", indent=25)
    pdf.bullet("Result is stored in the in-memory inventory (sorted by urgency)")
    pdf.bullet("Prediction is logged to MLflow with all metadata")
    pdf.bullet("Dashboard refreshes to show updated inventory")

    # ── 4. VISION MODEL ────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("4", "Vision Model")
    pdf.sub_title("Model Choice: CLIP (openai/clip-vit-base-patch32)")
    pdf.body_text(
        "CLIP (Contrastive Language-Image Pretraining) by OpenAI is a model that understands "
        "both images and text. It can classify images into arbitrary categories without any "
        "fine-tuning, using a technique called zero-shot classification."
    )
    pdf.body_text(
        "This is ideal for FruitQ because we need two types of classification from one model, "
        "and we don't need to collect and label training data."
    )

    pdf.sub_title("Step 1: Fruit Identification")
    pdf.body_text(
        "The model receives the image along with 25 candidate labels like 'a photo of a banana', "
        "'a photo of a mango', etc. It returns the most likely fruit type with a confidence score."
    )
    pdf.code_block(
        'FRUIT_TYPES = [\n'
        '    "apple", "banana", "mango", "orange",\n'
        '    "strawberry", "avocado", "peach", "pear",\n'
        '    "grapes", "watermelon", "kiwi", "pineapple",\n'
        '    "cherry", "blueberry", "papaya", ... (25 total)\n'
        ']'
    )

    pdf.sub_title("Step 2: Ripeness Classification")
    pdf.body_text(
        "The same model then classifies ripeness using four descriptive labels:"
    )
    pdf.code_block(
        'CANDIDATE_LABELS = [\n'
        '    "unripe green fruit",\n'
        '    "nearly ripe fruit",\n'
        '    "ripe ready-to-eat fruit",\n'
        '    "overripe spoiled fruit",\n'
        ']'
    )
    pdf.body_text(
        "The model returns confidence scores for each category. The highest-scoring label "
        "becomes the ripeness classification, and the shipping priority is derived from it."
    )

    pdf.sub_title("Why CLIP?")
    pdf.bullet("No training data needed - works out of the box")
    pdf.bullet("Single model handles both fruit ID and ripeness (efficient)")
    pdf.bullet("Runs locally on CPU - no GPU or cloud API required")
    pdf.bullet("Free and open-source via Hugging Face Transformers")
    pdf.bullet("~340 MB download, cached after first use")

    # ── 5. INVENTORY ────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("5", "Ripeness Ranking & Inventory")
    pdf.body_text(
        "The inventory module maintains a thread-safe, in-memory list of all analysed fruits. "
        "Every time a new fruit is added, the list is automatically re-sorted so the most "
        "ripe (most urgent) fruits appear first."
    )

    pdf.sub_title("Ranking Logic")
    pdf.body_text("Each ripeness label has a numeric rank:")
    widths3 = [45, 45, 45]
    pdf.table_row(["Label", "Rank", "Priority"], widths3, bold=True, fill=True)
    pdf.table_row(["Unripe", "0 (lowest)", "Not yet"], widths3)
    pdf.table_row(["Nearly Ripe", "1", "In 3 days"], widths3)
    pdf.table_row(["Ripe", "2", "Tomorrow"], widths3)
    pdf.table_row(["Overripe", "3 (highest)", "Today"], widths3)

    pdf.ln(3)
    pdf.body_text(
        "The inventory is sorted in descending order by rank, so overripe fruits always "
        "appear at the top. The summary endpoint provides counts per category and a "
        "ready-made 'ship today' list."
    )

    pdf.sub_title("Key Operations")
    pdf.bullet("add() - Insert a fruit and re-sort the inventory")
    pdf.bullet("get_all() - Return all fruits (most urgent first)")
    pdf.bullet("remove() - Remove a fruit after it ships")
    pdf.bullet("summary() - Counts by category + ship-today list")
    pdf.bullet("clear() - Reset the inventory")

    # ── 6. REST API ─────────────────────────────────────────────────────────
    pdf.section_title("6", "REST API (FastAPI)")
    pdf.body_text(
        "The API is the central hub. The dashboard, external clients, and automated systems "
        "all interact through these endpoints."
    )
    pdf.ln(2)
    widths4 = [25, 50, 95]
    pdf.table_row(["Method", "Path", "Description"], widths4, bold=True, fill=True)
    pdf.table_row(["POST", "/predict", "Upload image -> get ripeness + add to inventory"], widths4)
    pdf.table_row(["GET", "/inventory", "List all fruits ranked by ripeness"], widths4)
    pdf.table_row(["GET", "/inventory/summary", "Counts by category + ship-today list"], widths4)
    pdf.table_row(["DELETE", "/inventory/{id}", "Remove a fruit after shipping"], widths4)
    pdf.table_row(["GET", "/health", "Health check (returns {status: ok})"], widths4)

    pdf.ln(3)
    pdf.sub_title("Example: Predict Endpoint")
    pdf.code_block(
        "curl -X POST http://localhost:8000/predict \\\n"
        '  -F "file=@banana.jpg" \\\n'
        '  -F "fruit_name=banana"\n'
        "\n"
        "Response:\n"
        "{\n"
        '  "fruit_name": "Banana",\n'
        '  "detected_fruit": "Banana",\n'
        '  "fruit_confidence": 92.3,\n'
        '  "ripeness_label": "Ripe",\n'
        '  "confidence": 84.5,\n'
        '  "shipping_priority": "Tomorrow"\n'
        "}"
    )

    # ── 7. DASHBOARD ────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("7", "Dashboard UI (Streamlit)")
    pdf.body_text(
        "The Streamlit dashboard provides a user-friendly interface for uploading fruit images, "
        "viewing analysis results, and managing the inventory."
    )

    pdf.sub_title("Features")
    pdf.bullet("Sidebar: Image upload with drag-and-drop, optional fruit name override")
    pdf.bullet("Auto-detection: AI identifies the fruit type automatically")
    pdf.bullet("Result display: Ripeness label, confidence score, shipping priority")
    pdf.bullet("KPI row: Total fruits, ship-today count, ripe count, unripe count")
    pdf.bullet("Pie chart: Ripeness distribution (colour-coded donut chart via Plotly)")
    pdf.bullet("Inventory table: All fruits ranked by urgency with colour-coded shipping labels")
    pdf.bullet("Ship-today alerts: Red banners for fruits that must ship immediately")
    pdf.bullet("Remove buttons: Mark fruits as shipped and remove from inventory")

    # screenshot
    screenshot_path = os.path.join(os.path.dirname(__file__), "docs", "dashboard_screenshot.png")
    if os.path.exists(screenshot_path):
        pdf.ln(3)
        pdf.image(screenshot_path, x=15, w=180)

    # ── 8. MLFLOW ───────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("8", "MLflow Experiment Tracking")
    pdf.body_text(
        "Every prediction is logged as an MLflow run, creating a complete audit trail of "
        "model behaviour over time."
    )

    pdf.sub_title("What Gets Logged")
    widths5 = [50, 50, 70]
    pdf.table_row(["Type", "Field", "Example"], widths5, bold=True, fill=True)
    pdf.table_row(["Parameter", "image_filename", "banana.jpg"], widths5)
    pdf.table_row(["Parameter", "fruit_name", "Banana"], widths5)
    pdf.table_row(["Parameter", "ripeness_label", "Ripe"], widths5)
    pdf.table_row(["Parameter", "shipping_priority", "Tomorrow"], widths5)
    pdf.table_row(["Metric", "confidence", "84.5"], widths5)
    pdf.table_row(["Metric", "score_unripe", "3.1"], widths5)
    pdf.table_row(["Metric", "score_ripe", "84.5"], widths5)
    pdf.table_row(["Tag", "alert", "low_confidence (if < 60%)"], widths5)

    pdf.ln(3)
    pdf.sub_title("Low-Confidence Alerts")
    pdf.body_text(
        "If the model's confidence drops below 60%, the run is tagged with "
        "'alert: low_confidence' and a warning is logged. This helps identify images "
        "that the model struggles with, guiding future improvements."
    )

    # ── 9. DOCKER ───────────────────────────────────────────────────────────
    pdf.section_title("9", "Containerization (Docker)")
    pdf.body_text(
        "The application uses a multi-stage Docker build to keep the final image lean. "
        "A docker-compose file orchestrates the API, dashboard, and MLflow together."
    )

    pdf.sub_title("Why Docker?")
    pdf.bullet("Eliminates 'works on my machine' - identical environment everywhere")
    pdf.bullet("Azure Container Instances requires a Docker image to deploy")
    pdf.bullet("Dependencies are locked - no version conflicts on other machines")
    pdf.bullet("Easy to scale: run multiple API containers behind a load balancer")

    pdf.sub_title("Docker Compose Services")
    widths6 = [40, 40, 90]
    pdf.table_row(["Service", "Port", "Description"], widths6, bold=True, fill=True)
    pdf.table_row(["api", "8000", "FastAPI server (default CMD)"], widths6)
    pdf.table_row(["dashboard", "8501", "Streamlit UI (overrides CMD)"], widths6)
    pdf.table_row(["mlflow", "5000", "MLflow tracking UI"], widths6)

    # ── 10. CI/CD ───────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("10", "CI/CD Pipeline (GitHub Actions)")
    pdf.body_text(
        "The pipeline runs automatically on every push and consists of three jobs:"
    )

    pdf.sub_title("Job 1: Test")
    pdf.bullet("Sets up Python 3.11 with pip caching")
    pdf.bullet("Installs all dependencies from requirements.txt")
    pdf.bullet("Runs pytest on the full test suite")
    pdf.bullet("Tests mock the vision model - no GPU or internet needed")

    pdf.sub_title("Job 2: Build & Push")
    pdf.bullet("Sets up Docker Buildx for efficient caching")
    pdf.bullet("Logs into GitHub Container Registry (GHCR)")
    pdf.bullet("Builds the Docker image with GHA cache")
    pdf.bullet("On main branch: pushes to GHCR with sha and latest tags")

    pdf.sub_title("Job 3: Deploy (main only)")
    pdf.bullet("Sets up Terraform 1.8")
    pdf.bullet("Runs terraform init + terraform apply")
    pdf.bullet("Deploys to Azure Container Instances automatically")

    pdf.ln(3)
    pdf.code_block(
        "Pipeline Flow:\n"
        "\n"
        "  git push --> [Test] --> [Build Image] --> [Deploy to Azure]\n"
        "                pytest      Docker+GHCR      Terraform apply\n"
        "                              (main only)      (main only)"
    )

    # ── 11. TERRAFORM ───────────────────────────────────────────────────────
    pdf.section_title("11", "Cloud Deployment (Terraform + Azure)")
    pdf.body_text(
        "Infrastructure is defined as code using Terraform. A single 'terraform apply' "
        "creates all Azure resources needed to run the application in production."
    )

    pdf.sub_title("Resources Created")
    pdf.bullet("Azure Resource Group - logical container for all resources")
    pdf.bullet("Log Analytics Workspace - centralised logging and monitoring")
    pdf.bullet("Container Group (API) - runs the FastAPI server (1 CPU, 2 GB RAM)")
    pdf.bullet("Container Group (Dashboard) - runs Streamlit (0.5 CPU, 1 GB RAM)")

    pdf.sub_title("Required Azure Secrets (in GitHub)")
    widths7 = [60, 110]
    pdf.table_row(["Secret", "Description"], widths7, bold=True, fill=True)
    pdf.table_row(["ARM_CLIENT_ID", "Service principal client ID"], widths7)
    pdf.table_row(["ARM_CLIENT_SECRET", "Service principal secret"], widths7)
    pdf.table_row(["ARM_SUBSCRIPTION_ID", "Azure subscription ID"], widths7)
    pdf.table_row(["ARM_TENANT_ID", "Azure AD tenant ID"], widths7)

    # ── 12. HOW TO RUN ──────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("12", "How to Run")

    pdf.sub_title("Local Development")
    pdf.code_block(
        "# Clone and install\n"
        "git clone https://github.com/wasimahmadpk/fruitesQ.git\n"
        "cd fruitesQ\n"
        "pip install -r requirements.txt\n"
        "\n"
        "# Start the API (downloads model on first run)\n"
        "uvicorn src.api:app --reload --port 8000\n"
        "\n"
        "# Start the dashboard (in a second terminal)\n"
        "streamlit run src/dashboard.py\n"
        "\n"
        "# Start MLflow UI (optional, third terminal)\n"
        "mlflow ui --port 5000"
    )

    pdf.sub_title("With Docker")
    pdf.code_block(
        "# Run everything with docker-compose\n"
        "docker compose up\n"
        "\n"
        "# Or run just the API\n"
        "docker build -t fruitq .\n"
        "docker run -p 8000:8000 fruitq"
    )

    pdf.sub_title("Run Tests")
    pdf.code_block("pytest tests/ -v")

    pdf.sub_title("Access Points")
    widths8 = [60, 110]
    pdf.table_row(["Service", "URL"], widths8, bold=True, fill=True)
    pdf.table_row(["API Docs (Swagger)", "http://localhost:8000/docs"], widths8)
    pdf.table_row(["Dashboard", "http://localhost:8501"], widths8)
    pdf.table_row(["MLflow UI", "http://localhost:5000"], widths8)
    pdf.table_row(["Health Check", "http://localhost:8000/health"], widths8)

    # ── 13. PROJECT STRUCTURE ───────────────────────────────────────────────
    pdf.section_title("13", "Project Structure")
    pdf.code_block(
        "fruitesQ/\n"
        "  src/\n"
        "    api.py            FastAPI endpoints\n"
        "    model.py          CLIP vision model (ID + ripeness)\n"
        "    inventory.py      Ranked inventory management\n"
        "    dashboard.py      Streamlit dashboard UI\n"
        "  tests/\n"
        "    test_api.py       API integration tests\n"
        "    test_inventory.py Inventory unit tests\n"
        "  .github/workflows/\n"
        "    ci.yml            GitHub Actions CI/CD pipeline\n"
        "  terraform/\n"
        "    main.tf           Azure infrastructure as code\n"
        "  mlflow_tracking.py  MLflow logging helpers\n"
        "  Dockerfile          Multi-stage Docker build\n"
        "  docker-compose.yml  All services together\n"
        "  requirements.txt    Python dependencies\n"
        "  README.md           Project documentation"
    )

    # ── OUTPUT ──────────────────────────────────────────────────────────────
    out_path = os.path.join(os.path.dirname(__file__), "docs", "FruitQ_Project_Documentation.pdf")
    pdf.output(out_path)
    print(f"PDF saved to: {out_path}")


if __name__ == "__main__":
    build_pdf()
