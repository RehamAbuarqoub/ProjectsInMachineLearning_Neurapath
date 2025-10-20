# NeuraPath — Projects in Machine Learning
_AI-powered mock interview coach with resume parsing, career pathing, and personalized learning._

---

## 🔎 Project Overview
**NeuraPath** helps students and early-career professionals improve interview readiness and employability with three core features:
1) **Resume Parsing & Feedback** — extract skills/experience from uploaded resumes and provide actionable critique.  
2) **Career Path Recommendation** — map current skills to realistic next roles and multi-step career journeys.  
3) **Personalized Learning Recommendation** — suggest courses/projects to close skill gaps toward target roles.

**Goals**
- Deliver a working prototype with reproducible pipelines and API.
- Maintain a structured backlog (Features → Stories → Tasks) aligned to the three use cases.
- Integrate Azure DevOps Boards with GitHub so PRs/commits link to work items (`AB#<id>`).

**Key Links (fill before submission)**
- **Azure DevOps Boards:** <ADD_DEVOPS_BOARDS_URL>  
- **GitHub Repository:** <ADD_GITHUB_REPO_URL>  
- **Instructor-Approved PR:** <ADD_PR_URL> (include `AB#<id>` in title/desc)  

---

## 🧩 Use Cases (Features)
> These correspond to **Features** in Azure DevOps; each has Stories and Tasks in the backlog.

### 1) Resume Parsing & Feedback (Skill Extraction + Critique)
- **Gap:** Unstructured resumes and inconsistent feedback prevent reliable skill assessment.  
- **Critical Point of Occurrence:** When the user uploads a resume.  
- **Countermeasure (Tech):** NLP stack (NER + embeddings) for skill/entity extraction, ontology for skill normalization, and rubric-based critique with XAI highlights.  
- **Target:** Actionable resume feedback and normalized skill vectors for downstream modules.

### 2) Career Path Recommendation (Role Transition Mapping)
- **Gap:** Users struggle to see realistic next roles and the steps to reach them.  
- **Critical Point of Occurrence:** After skills are extracted and a target role/industry is selected.  
- **Countermeasure (Tech):** Career graph + embedding similarity + pathfinding over roles with explainable justifications.  
- **Target:** Recommend feasible 1–2 step transitions with ≥70% skill overlap and explicit gaps to fill.

### 3) Personalized Learning Recommendation (Adaptive Skill-Building)
- **Gap:** Generic learning advice; no linkage from gaps to concrete resources.  
- **Critical Point of Occurrence:** After target roles and gaps are known.  
- **Countermeasure (Tech):** Hybrid recommenders (content + collaborative + embeddings), constraint-aware filtering (time, cost, level).  
- **Target:** Top-5 recommendations with high relevance and measurable progression toward the target role.

---

## 🗂️ Repository Structure
```
.
├─ src/
│  ├─ data/            # loaders, validators, sample catalogs
│  ├─ features/        # preprocessing (encoders, tokenizers)
│  ├─ models/          # model builders (classical/LLM/ranker)
│  ├─ training/        # train/eval loops, metrics, checkpoints
│  ├─ api/             # FastAPI app (scoring + endpoints)
│  └─ utils/           # logging, config, seeds, helpers
├─ notebooks/
│  ├─ 01_eda.ipynb
│  ├─ 02_train_baselines.ipynb
│  └─ 03_eval_error_analysis.ipynb
├─ data/               # local only (gitignored)
│  ├─ raw/
│  └─ processed/
├─ results/            # figures, tables, reports, checkpoints
├─ tests/              # unit tests
├─ .github/workflows/  # CI (lint/tests) (optional)
├─ requirements.txt
├─ README.md
└─ LICENSE
```

---

## ⚙️ Setup

### 1) Prerequisites
- Python 3.10+ and Git
- (Recommended) Conda or venv
- Windows: if `pip` is not recognized, use `py -m pip ...`

### 2) Clone
```bash
git clone <ADD_GITHUB_REPO_URL> neurapath-ml
cd neurapath-ml
```

### 3) Create Environment
**Conda**
```bash
conda create -n neurapath python=3.10 -y
conda activate neurapath
```
**venv (Linux/Mac)**
```bash
python3 -m venv .venv
source .venv/bin/activate
```
**venv (Windows PowerShell)**
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 4) Install Deps
```bash
# If pip is available
pip install -r requirements.txt

# Windows fallback if pip isn't recognized
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

### 5) Configure Environment
Create a `.env` file (used by API and notebooks):
```
# .env
OPENAI_API_KEY=<if using LLMs>
MODEL_DIR=./results/checkpoints
DATA_DIR=./data
```

---

## 🚀 Usage Examples

### A) Quick EDA (Notebook)
Open `notebooks/01_eda.ipynb` and run all cells.  
VS Code tip: select the `neurapath` environment as the interpreter.

### B) Train a Baseline
```bash
python -m src.training.train \
  --use_case "mock_interview_scoring" \
  --model "xgboost" \
  --data_path "./data/processed/mock_interview.csv" \
  --val_split 0.2 \
  --seed 42 \
  --output_dir "./results/baselines"
```
**Outputs:** metrics JSON, model artifact, plots under `./results/baselines`.

### C) Evaluate on Holdout
```bash
python -m src.training.evaluate \
  --artifact "./results/baselines/model.bin" \
  --test_path "./data/processed/mock_interview_test.csv" \
  --report_path "./results/baselines/test_report.json"
```

### D) Run the API (FastAPI)
```bash
uvicorn src.api.app:app --reload --port 8000
```
Open `http://localhost:8000/docs` for interactive endpoints.  
**Example request:**
```bash
curl -X POST "http://localhost:8000/score/mock" -H "Content-Type: application/json" -d '{
  "transcript": "Tell me about yourself...",
  "rubric_version": "v1.1"
}'
```

---

## 📅 Sprints, Backlog & Capacity (DevOps)
- **Sprints 1–3** created in ADO with term dates; visible on the Task Board.
- **Backlog** structured: each **Use Case = Feature**, with **Stories** and **Tasks** beneath.
- **Capacity planning:** for **S1–S3**, every teammate has ≥1 task with **Remaining Work (hrs)** and **Activity** set.
- **UAT definition:** each Feature includes a **Story named “Internal Review”** and on that story a **Task named “User Acceptance Testing” (UAT)**.

**URLs to include in submission**
- Boards (Task Board & Backlog): <ADD_DEVOPS_BOARDS_URL>  
- Example Work Item with PR link: <ADD_AB_ITEM_URL>  
- PR with `AB#<id>` reference: <ADD_PR_URL>

---

## 🔗 Azure DevOps ↔ GitHub Integration (How-to)
1. GitHub repo → **Settings → Integrations**: install **Azure Boards** app.  
2. ADO → **Project Settings → Boards → GitHub connections → New connection**: authorize repo.  
3. Reference ADO work items in commits/PRs with `AB#<id>` (e.g., `feat: calibrate rubric (AB#123)`).  
4. Verify in ADO work item (**Development** section shows PR/commit).  
5. Verify in GitHub PR (**Linked work items** panel shows AB# and status).

---

## 🤝 Collaboration & Communication
- **DevOps:** comments on work items; use **Tags**, **Priority**, **Area**.  
- **GitHub:** PR reviews; CODEOWNERS/branch protection (optional); Discussions for decisions.  
- **Wiki/Docs:** architecture, data dictionary, and API contracts kept up-to-date.  
- **Standup:** <DAYS/TIME> • **Channel:** <Teams/Slack link> • **Instructor Access:** invited to ADO + repo.

---

## ✅ Testing
```bash
pytest -q
```
Optional:
```bash
pip install pytest-cov
pytest --cov=src --cov-report=term-missing
```

---

## 🧪 Data Notes
- Store raw files in `data/raw/` (gitignored).  
- Use `src/data` loaders to produce `data/processed`.  
- Prevent leakage: split **before** target-aware transforms.

---

## 🧰 Troubleshooting
**pip not recognized (Windows)** → use `py -m pip ...` and ensure Python on PATH.  
**Notebook kernel missing** → select the correct interpreter (your env).  
**Torch/CUDA issues** → use CPU wheel or match CUDA version per docs.

---

## 📝 License
MIT (or course default).

---

## 👥 Team & Roles
- Mandeep Singh Brar — ML Product Manager (backlog, targets, ADO hygiene, demos)  
- <Teammate 2> — ML Engineer (models, experiments, metrics, MLOps handoff)  
- <Teammate 3> — Data Engineer (ETL, feature store, data quality)  
- <Teammate 4> — App/Frontend (API/UI integration, UX tests)
