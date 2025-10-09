# 🧊 The Coding Penguins — Automated Entity Extraction (Deviathon 2025)

A generative AI-powered system that automatically **extracts key entities** such as **Ministers, Judges, and Officials** from any given web domain.  
It combines **web crawling**, **NLP entity extraction**, and an interactive **Streamlit UI** for visualization.

Built by **Team The Coding Penguins** for **Deviathon 2025**.

---

## 👨‍💻 Team

| Name | Role | Responsibilities |
|------|------|------------------|
| 🐧 **Prakarsh Kaushik** | Team Lead & Backend/NLP | FastAPI backend, NLP extractor, integration |
| 🐧 **Om Upadhyay** | Crawler Developer | Web crawling & data collection |
| 🐧 **Pratiksha** | NLP & Rules | spaCy model tuning & entity linking |
| 🐧 **Priyanshu Gautam** | Frontend Developer | Streamlit UI & visualization |

---

## ⚙️ Tech Stack

- **Language:** Python 3.12  
- **Backend:** FastAPI  
- **Frontend:** Streamlit  
- **NLP:** spaCy (+ rule-based title matcher)  
- **Crawler:** Requests + BeautifulSoup  
- **Deployment:** Docker Compose (optional)

---

## 🚀 Features

- Crawl a domain and collect pages (JSONL)
- Extract PERSON ↔ TITLE pairs (e.g., “Rahul Sharma — Minister of Education”)
- REST API for `/crawl`, `/extract`, `/results`
- Streamlit UI to run and visualize results
- Download structured JSON report

---

## 📁 Project Structure

```text
The Coding Penguins/
│
├── api/                      # FastAPI backend
│   ├── main.py
│   ├── schemas.py
│   └── __init__.py
│
├── extractor/                # NLP extractor
│   ├── nlp_pipeline.py
│   ├── rules.py
│   └── __init__.py
│
├── crawler/                  # Web crawler (Om)
│   └── scraper.py
│
├── ui/                       # Streamlit frontend
│   └── app.py
│
├── data/                     # Input/output data
│   ├── pages.jsonl
│   └── entities.json
│
├── docs/                     # Documentation
│   ├── crawler-contract.md
│   └── architecture.md
│
├── docker/                   # (optional) Docker setup
│   ├── api.Dockerfile
│   ├── ui.Dockerfile
│   └── docker-compose.yml
│
├── requirements.txt
├── .gitignore
└── README.md
````

---

## 🧠 How It Works

1. **Crawl** → Save pages to `data/pages.jsonl` (one JSON per line).
2. **Extract** → spaCy NER + title rules → `data/entities.json`.
3. **Serve** → FastAPI exposes endpoints.
4. **Visualize** → Streamlit UI shows and exports results.

---

## 💻 Run Locally

### 1) Clone & Setup

```bash
git clone https://github.com/PrakarshKaushik11/The-Coding-Penguins-Deviathon-2025.git
cd The-Coding-Penguins-Deviathon-2025
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2) Start the Backend API

```bash
uvicorn api.main:app --reload --port 8000
```

Open Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 3) Start the Frontend UI

```bash
streamlit run ui/app.py
```

Open: [http://localhost:8501](http://localhost:8501)

### 4) Try It

* Click **Run Extraction** (uses `data/pages.jsonl`).
* Click **Refresh Results** to view entities.
* **Download JSON** to save the output.

---

## 🧰 API Endpoints

| Method | Endpoint   | Description                       |
| -----: | ---------- | --------------------------------- |
|    GET | `/health`  | API health check                  |
|   POST | `/crawl`   | Crawl domain → `data/pages.jsonl` |
|   POST | `/extract` | Run NLP → `data/entities.json`    |
|    GET | `/results` | Return extracted entities JSON    |

---

## 🐍 Requirements

Install all dependencies:

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

---

## 🐳 Docker (Optional)

```bash
docker-compose up --build
```

* Backend: [http://127.0.0.1:8000](http://127.0.0.1:8000)
* Frontend: [http://localhost:8501](http://localhost:8501)

---

## 🏁 Status

* ✅ Backend, NLP, and UI integrated
* ⚙️ Crawler module in progress (Om)
* 🚀 Ready for demo

---

## 🧑‍⚖️ License

MIT License © 2025 — **Team The Coding Penguins**