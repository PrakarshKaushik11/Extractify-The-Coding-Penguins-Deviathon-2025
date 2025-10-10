# 🧠 Automated Domain-Specific Entity Extraction and Information Structuring System  
### by **Team The Coding Penguins 🐧** — Deviathon 2025  

A local **AI-powered web intelligence system** that automatically crawls any website, extracts domain-specific entities, and structures them into meaningful insights — **without using cloud APIs**.  
It combines **focused web crawling**, **NLP-based entity extraction**, and **semantic ranking**, visualized in an interactive **Streamlit dashboard**.  

---

## 👨‍💻 Team

| Name | Role | Responsibilities |
|------|------|------------------|
| 🐧 **Prakarsh Kaushik** | Team Lead & Backend/NLP | FastAPI backend, NLP extractor, integration |
| 🐧 **Om Upadhyay** | Web Crawler Developer | Focused crawler, domain parsing, data collection |
| 🐧 **Pratiksha** | NLP & Entity Logic | spaCy tuning, rule-based and semantic extraction |
| 🐧 **Priyanshu Gautam** | Frontend Developer | Streamlit UI, API integration, visualization |

---

## ⚙️ Tech Stack

- **Language:** Python 3.12  
- **Backend:** FastAPI  
- **Frontend:** Streamlit  
- **NLP Engine:** spaCy + Sentence Transformers (local semantic AI)  
- **Crawler:** Requests + BeautifulSoup + Rule-based traversal  
- **Ranking:** Hybrid model (BM25 + Semantic similarity)  
- **Deployment:** Docker (optional)

---

## 🚀 Features

✅ Intelligent domain crawling with depth and page control  
✅ AI-based entity extraction using local NLP and embeddings  
✅ Flexible — works with *any* domain and keyword context  
✅ Hybrid keyword + semantic ranking for accuracy  
✅ Streamlit dashboard for user-friendly visualization  
✅ 100% offline — no external LLM or cloud dependency  

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
├── crawler/                  # Web crawler (Om)
│   └── scraper.py
│
├── extractor/                # NLP & semantic extractor
│   ├── nlp_pipeline.py
│   └── __init__.py
│
├── ui/                       # Streamlit frontend
│   └── app.py
│
├── data/                     # Sample crawled & extracted data
│   ├── pages.jsonl
│   └── entities.json
│
├── requirements.txt
├── .gitignore
└── README.md
````

---

## 🧠 How It Works

1. **Crawl** → The crawler scans the domain and collects HTML/text content up to a defined depth and limit.
2. **Extract** → The NLP pipeline identifies meaningful entities using spaCy, rule-based patterns, and semantic embedding similarity.
3. **Rank** → Hybrid model using **BM25 + Sentence Transformers** ranks relevant entities by confidence.
4. **Visualize** → Streamlit UI displays the extracted entities, scores, and snippets interactively.

---

## 💻 Run Locally

### 1️⃣ Clone and Setup

```bash
git clone https://github.com/PrakarshKaushik11/The-Coding-Penguins-Deviathon-2025.git
cd The-Coding-Penguins-Deviathon-2025
python -m venv .venv

# Activate the environment
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

---

### 2️⃣ Start the Backend (FastAPI)

```bash
set PYTHONPATH=%CD%
python -m uvicorn api.main:app --reload --port 8000
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for Swagger API view.

---

### 3️⃣ Start the Frontend (Streamlit)

In a new terminal window:

```bash
cd "D:\The Coding Penguins"
.\.venv\Scripts\activate
streamlit run ui/app.py
```

Then open [http://localhost:8501](http://localhost:8501).

---

### 4️⃣ Try It!

* Enter any domain, e.g. `https://www.gla.ac.in/alumni`
* (Optional) Add keywords like `alumni, graduate, batch of, class of`
* Enable **Semantic AI**
* Click **Crawl & Extract**
* View structured entities with scores and snippets.

---

## 🧰 API Endpoints

|  Method  | Endpoint             | Description                             |
| :------: | :------------------- | :-------------------------------------- |
|  **GET** | `/health`            | API health check                        |
| **POST** | `/crawl`             | Crawl domain and return collected pages |
| **POST** | `/crawl-and-extract` | Crawl + NLP + Semantic extraction       |
|  **GET** | `/results`           | Return extracted entities JSON          |

---

## 🧩 Example Workflow

```bash
# Crawl + extract in one step
curl -X POST http://127.0.0.1:8000/crawl-and-extract \
-H "Content-Type: application/json" \
-d "{\"domain\": \"https://www.justice.gov\", \"keywords\": [\"minister\", \"judge\"], \"max_pages\": 20, \"max_depth\": 1}"
```

---

## 🧱 Architecture Overview

```
[ Streamlit UI ] 
        ↓
[ FastAPI Backend ]
        ↓
[ Focused Web Crawler ]
        ↓
[ NLP + Semantic Extractor (spaCy + Sentence Transformers) ]
        ↓
[ Ranked Entities & Structured Output ]
```

---

## 🧰 Requirements

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

---

## 🐳 Docker (Optional)

```bash
docker-compose up --build
```

* Backend → [http://127.0.0.1:8000](http://127.0.0.1:8000)
* Frontend → [http://localhost:8501](http://localhost:8501)

---

## 🏁 Current Status

✅ Backend, Crawler, Extractor, and UI integrated
✅ Semantic ranking implemented using local AI
✅ 100% offline execution
🚧 Future work — Entity linking, summarization, and Docker deployment

---

## 🧩 Problem It Solves

Extracting meaningful information from unstructured web data is slow, inconsistent, and domain-dependent.
Our system automates this by combining web crawling with AI-based entity understanding, enabling adaptive extraction for *any* domain — efficiently, privately, and offline.

---

## ⚙️ Challenges Faced

Building a flexible crawler for diverse site structures, ensuring accurate extraction without noise, optimizing local AI models under limited resources, and integrating backend + UI seamlessly — all while maintaining speed and accuracy.

---

## 📜 License

MIT License © 2025 — **Team The Coding Penguins 🐧**

