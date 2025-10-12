# 🧠 Extractify — The Coding Penguins Project (Deviathon 2025)

> ⚡ Crawl → Extract → Understand any domain using local AI  
> An **intelligent, offline information structuring system** that turns raw, unstructured website data into clean, organized knowledge.

---

## 🧩 Overview

**Extractify** is a full-stack AI system built for **Deviathon 2025** by *Team The Coding Penguins*.  
It automatically **crawls a domain**, **extracts key entities** (like Ministers, Judges, Officials, Professors), and **structures them** into a readable, exportable dataset — all **locally**, without needing any cloud services.

This project focuses on **domain-specific entity extraction** using a hybrid approach that combines:
- **spaCy NLP**
- **Regex pattern matching**
- **Zero-shot classification**

---

## ✨ Key Features

| Feature | Description |
|----------|-------------|
| 🕷️ **Automated Web Crawling** | Custom-built breadth-first crawler with link filtering and keyword-based targeting. |
| 🧠 **AI Entity Extraction** | Combines **spaCy**, regex, and zero-shot learning for high-accuracy entity recognition. |
| ⚡ **Offline Execution** | Works completely locally — no external API calls or internet AI dependencies. |
| 📊 **Structured Output** | Exports entities into **JSON format** for further use or integration. |
| 💻 **Interactive UI** | Modern React + Tailwind dashboard to monitor progress and view results. |
| 🔒 **Privacy-Centric** | All crawling and extraction happens locally on your machine. |

---

## 🏗️ Architecture

```

Frontend (React + Tailwind)
│
▼
FastAPI Backend  ←→  NLP Extractor (spaCy + Regex + Zero-shot)
│
▼
Crawler (Requests + BeautifulSoup)
│
▼
JSON Storage + Result Export

````

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-------------|
| **Frontend** | React (Vite), Tailwind CSS, shadcn/ui, Framer Motion |
| **Backend** | FastAPI, Uvicorn |
| **NLP Engine** | spaCy 3.8, Regex, SentenceTransformer (Zero-shot) |
| **Crawler** | BeautifulSoup, Requests |
| **Storage** | Local JSON files (`data/pages.jsonl`, `data/entities.json`) |
| **Version Control** | Git + GitHub |
| **Execution** | Local environment (no cloud dependencies) |

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/PrakarshKaushik11/Extractify-The-Coding-Penguins-Deviathon-2025.git
cd "Extractify - The Coding Penguins Project Deviathon 2025"
````

---

### 2️⃣ Backend Setup (FastAPI)

```bash
cd api
python -m venv .venv
.venv\Scripts\activate   # On Windows
# or
source .venv/bin/activate   # On Mac/Linux

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Your backend will now run at:
➡️ **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

### 3️⃣ Frontend Setup (React + Vite)

```bash
cd ui
npm install
npm run dev
```

Your frontend runs at:
➡️ **[http://localhost:8080](http://localhost:8080)**

---

### 4️⃣ Typical Workflow

1. Launch both backend and frontend
2. Open the UI in your browser
3. Enter a **target domain** (e.g. `https://www.codingblocks.com`)
4. Set **max pages** and **crawl depth**
5. Click **Start Crawl**
6. The system crawls → extracts entities → displays structured results
7. Export results as **JSON** from the Results page

---

## 📂 Core Files

| Path                              | Description                                               |
| --------------------------------- | --------------------------------------------------------- |
| `/api/main.py`                    | FastAPI backend routes (`/crawl`, `/extract`, `/results`) |
| `/crawler/scraper.py`             | Domain crawler with BFS traversal & keyword filtering     |
| `/extractor/nlp_pipeline.py`      | NLP entity extraction pipeline                            |
| `/ui/src/pages/CrawlSettings.tsx` | Crawl configuration screen                                |
| `/ui/src/pages/Extraction.tsx`    | Real-time extraction view                                 |
| `/ui/src/pages/Results.tsx`       | Results dashboard + JSON export                           |
| `/ui/src/lib/api.ts`              | Frontend-backend connector                                |
| `/data/pages.jsonl`               | Stores crawled pages temporarily                          |
| `/data/entities.json`             | Stores extracted entities                                 |

---

## 🧠 Example Output

```json
[
  {
    "name": "John Doe",
    "type": "Judge",
    "url": "https://www.justice.gov/news/john-doe-appointed",
    "snippet": "President announced John Doe as the new federal judge...",
    "score": 0.92
  },
  {
    "name": "Dr. Alice Smith",
    "type": "Professor",
    "url": "https://www.university.edu/faculty/alice-smith",
    "snippet": "Dr. Alice Smith specializes in AI and ethics...",
    "score": 0.89
  }
]
```

---

## 💻 UI Highlights

| Section               | Description                                        |
| --------------------- | -------------------------------------------------- |
| 🏠 **Home**           | Start button to begin crawl & extraction           |
| ⚙️ **Crawl Settings** | Domain, keywords, page & depth configuration       |
| 🤖 **AI Extraction**  | Live progress updates and analysis logs            |
| 📊 **Results**        | Table view of all extracted entities + JSON export |

---

## 👩‍💻 Team — *The Coding Penguins*

| Member                  | Role                      | Contribution                                 |
| ----------------------- | ------------------------- | -------------------------------------------- |
| 🧠 **Prakarsh Kaushik** | Team Lead / Backend + NLP | Designed FastAPI backend and NLP integration |
| 🕷️ **Om Upadhyay**     | Web Crawler Developer     | Built the crawler (BFS + keyword filtering)  |
| 🧩 **Pratiksha**        | NLP Engineer              | Designed and refined entity extraction logic |
| 💻 **Priyanshu Gautam** | Frontend Developer        | Built modern React + Tailwind UI             |

---

## 🏁 License

This project is licensed under the **MIT License** —
You’re free to use, modify, and enhance it with credit to the original authors.

---

## 💙 Acknowledgements

* Built with ❤️ by **The Coding Penguins** for **Deviathon 2025**
* Powered by **FastAPI**, **spaCy**, and **React**
* Special thanks to our mentors, organizers, and judges for their guidance

---


