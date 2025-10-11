
# 🐧 The Coding Penguins — Automated Domain-Specific Entity Extraction System

> ⚡ Crawl → Extract → Understand any domain using local AI  
> An **offline, intelligent information structuring system** that transforms unstructured web data into meaningful, organized knowledge.



---

## 🧠 Overview

**The Coding Penguins** is a full-stack AI system built for **Deviathon 2025** that automatically crawls a web domain, extracts relevant entities (e.g., *Ministers, Judges, Officials, Professors*), and structures them into a clean dataset.

It operates entirely offline using **local AI models (spaCy + rule-based + zero-shot)**, ensuring **privacy, speed, and reliability** — perfect for domain-specific knowledge discovery.

---

## ✨ Key Features

| Feature | Description |
|----------|--------------|
| 🕷️ **Automated Web Crawling** | Intelligent breadth-first crawler with depth control and keyword filtering. |
| 🧩 **AI-Powered Entity Extraction** | Hybrid NLP pipeline combining **spaCy**, regex, and zero-shot classification. |
| 📊 **Structured Knowledge Output** | Clean JSON & visual display of extracted entities for analysis or export. |
| ⚡ **Fast & Local** | Fully offline inference, no external APIs required. |
| 🧠 **Real-Time UI** | Beautiful React dashboard for progress, stats, and results. |
| 🔒 **Privacy-Friendly** | No data leaves your system — all AI models run locally. |

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
SQLite / JSON Storage  ←→  UI Visualization

````

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-------------|
| **Frontend** | React (Vite), Tailwind CSS, shadcn/ui, Framer Motion |
| **Backend** | FastAPI, Uvicorn |
| **NLP Engine** | spaCy 3.8, Regex, SentenceTransformer (Zero-shot) |
| **Crawler** | BeautifulSoup, Requests |
| **Database** | JSONL + SQLite (optional) |
| **Deployment** | Local / Docker (optional) |
| **Version Control** | Git + GitHub |

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/the-coding-penguins.git
cd the-coding-penguins
````

---

### 2️⃣ Backend Setup (FastAPI)

```bash
cd api
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend runs at:
➡️ **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

### 3️⃣ Frontend Setup (React + Vite)

```bash
cd ui
npm install
npm run dev
```

Frontend runs at:
➡️ **[http://localhost:5173](http://localhost:5173)**

---

### 4️⃣ Workflow

1. Open the UI
2. Enter a **domain** (e.g. `https://www.justice.gov`)
3. Set **crawl depth & max pages**
4. Click **Start Crawl** → system crawls + extracts entities
5. View **AI Extraction progress** → then view **Results**

---

## 🧩 Core Files

| Path                              | Description                                                  |
| --------------------------------- | ------------------------------------------------------------ |
| `/api/main.py`                    | FastAPI backend endpoints (`/crawl`, `/extract`, `/results`) |
| `/crawler/scraper.py`             | Domain crawler with BFS, keyword-based link filtering        |
| `/extractor/nlp_pipeline.py`      | spaCy + rule-based + transformer NLP extractor               |
| `/ui/src/pages/CrawlSettings.tsx` | Crawl configuration screen                                   |
| `/ui/src/pages/Extraction.tsx`    | Real-time AI extraction status                               |
| `/ui/src/pages/Results.tsx`       | Entity result viewer with search & stats                     |
| `/ui/src/lib/api.ts`              | API connector for backend communication                      |

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

## 🧩 UI Highlights

| Section               | Description                                         |
| --------------------- | --------------------------------------------------- |
| 🏠 **Home**           | Introduction + Start Extraction button              |
| ⚙️ **Crawl Settings** | Domain input, keyword filter, page/depth sliders    |
| 🤖 **AI Extraction**  | Real-time progress + log + confidence updates       |
| 📊 **Results**        | Structured entity table with search, stats & export |

---

## 🧑‍💻 Team — *The Coding Penguins*

| Member               | Role                      | Contribution                                    |
| -------------------- | ------------------------- | ----------------------------------------------- |
| **Prakarsh Kaushik** | Team Lead / Backend + NLP | FastAPI backend, NLP extraction integration     |
| **Om Upadhyay**      | Web Crawler Developer     | Built the crawling module with BFS logic        |
| **Pratiksha**        | NLP Engineer              | Designed and fine-tuned entity extraction rules |
| **Priyanshu Gautam** | Frontend Developer        | Built React + Tailwind UI, extraction dashboard |

---

## 📅 Timeline (Deviathon 2025)

| Phase       | Duration  | Deliverables                    |
| ----------- | --------- | ------------------------------- |
| **Phase 1** | Aug 2025  | Core backend (crawl + extract)  |
| **Phase 2** | Sept 2025 | Streamlit → React migration     |
| **Phase 3** | Oct 2025  | UI polish, integration, testing |
| **Phase 4** | Nov 2025  | Final deployment & presentation |

---

## 🧰 Future Improvements

* [ ] Add **semantic entity linking** across pages
* [ ] Include **LLM-assisted classification** (offline)
* [ ] Add **Docker Compose** for one-click deployment
* [ ] Support **visual graph view** of entities and relations

---

## 🏁 License

This project is open-source under the **MIT License**.
Feel free to modify, improve, and extend!

---

## ⭐ Acknowledgements

* Built with 💙 by **The Coding Penguins** for **Deviathon 2025**
* Powered by **FastAPI**, **spaCy**, and **React**
* Special thanks to mentors and judges for guidance & feedback
