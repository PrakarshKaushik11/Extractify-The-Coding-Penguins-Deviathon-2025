# 🧠 Extractify — The Coding Penguins Project (Deviathon 2025)

> ⚡ Crawl → Extract → Understand any domain using local AI  
> An **intelligent, offline information structuring system** that turns raw, unstructured website data into clean, organized knowledge.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Node.js 18+ (npm or bun)
- Git

### Installation & Running

```powershell
# 1. Clone the repository
git clone https://github.com/PrakarshKaushik11/Extractify-The-Coding-Penguins-Deviathon-2025.git
cd "Extractify - The Coding Penguins Project Deviathon 2025"

# 2. Backend Setup
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate    # Mac/Linux

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 3. Frontend Setup (in a new terminal)
cd ui
npm install  # or: bun install

# 4. Start Backend (terminal 1)
python -m uvicorn api.main:app --host 127.0.0.1 --port 8001 --reload

# 5. Start Frontend (terminal 2)
cd ui
npm run dev  # or: bun run dev
```

**Access the application:**
- 🌐 **Frontend UI:** http://localhost:8080
- 📚 **Backend API Docs:** http://127.0.0.1:8001/docs
- ❤️ **Health Check:** http://127.0.0.1:8001/api/health

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

## 📖 How to Use

### Workflow

1. **Launch the application** (both backend and frontend)
2. **Open the UI** in your browser at http://localhost:8080
3. **Navigate to Crawl Settings** page
4. **Configure crawl parameters:**
   - Enter a **target domain** (e.g., `https://www.geeksforgeeks.org`)
   - Add **keywords** (comma-separated, e.g., `faculty, professor, teacher`)
   - Set **max pages** (10-500) and **crawl depth** (1-5)
5. **Click "Start Crawl"** — the system will:
   - Crawl the domain and collect pages
   - Extract entities using AI/NLP
   - Display real-time progress
6. **View Results** — see extracted entities in a dynamic table
7. **Export Data** — download results as CSV or JSON

### Tips for Best Results

- Use specific keywords related to your target entities
- Start with smaller page counts (50-100) for testing
- Increase depth for deeper site exploration
- Check the "AI Extraction" page for real-time progress

---

## 📂 Project Structure

```
Extractify/
├── api/
│   ├── main.py              # FastAPI backend routes & logic
│   ├── validators.py        # Input validation utilities
│   └── __init__.py
├── crawler/
│   ├── scraper.py           # Web crawler with BFS traversal
│   └── __init__.py
├── extractor/
│   ├── nlp_pipeline.py      # AI/NLP entity extraction engine
│   └── __init__.py
├── ui/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.tsx              # Landing page
│   │   │   ├── CrawlSettings.tsx    # Crawl configuration
│   │   │   ├── Extraction.tsx       # Real-time extraction view
│   │   │   ├── Results.tsx          # Results table + export
│   │   │   └── SystemInfo.tsx       # System information
│   │   ├── components/
│   │   │   ├── Navigation.tsx       # Top navigation bar
│   │   │   └── StatCard.tsx         # Stats display component
│   │   ├── lib/
│   │   │   └── api.ts               # Frontend API client
│   │   └── App.tsx
│   ├── public/              # Static assets
│   └── package.json
├── data/
│   ├── pages.jsonl          # Crawled pages (temporary)
│   └── entities.json        # Extracted entities (output)
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
├── .gitignore              # Git ignore rules
├── LICENSE                 # MIT License
└── README.md               # This file
```

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

## 🎯 Features in Detail

### 🕷️ Smart Web Crawler
- **BFS (Breadth-First Search)** traversal for systematic page discovery
- **Keyword-based prioritization** for relevant pages
- **Respects robots.txt** (can be disabled for testing)
- **Configurable depth and page limits**
- **Rate limiting** to avoid overwhelming servers

### 🧠 AI-Powered Entity Extraction
- **spaCy NLP** for named entity recognition
- **Semantic scoring** using SentenceTransformers
- **Context-aware extraction** with surrounding text analysis
- **Regex patterns** for phone numbers, addresses, years
- **Duplicate detection and merging**
- **Confidence scoring** for each entity

### 💻 Modern Web Interface
- **Responsive design** with Tailwind CSS
- **Real-time progress tracking** during crawl/extraction
- **Dynamic table rendering** based on extracted fields
- **CSV/JSON export** capabilities
- **Stats dashboard** with entity counts and metrics
- **Dark theme** for comfortable viewing

---

## � Team — *The Coding Penguins*

<table>
  <tr>
    <td align="center">
      <h3>🧠 Prakarsh Kaushik</h3>
      <p><b>Team Lead | Backend & NLP</b></p>
      <p>FastAPI backend architecture<br>NLP pipeline integration<br>Project coordination</p>
    </td>
    <td align="center">
      <h3>🕷️ Om Upadhyay</h3>
      <p><b>Crawler Developer</b></p>
      <p>Web crawler implementation<br>BFS algorithm & optimization<br>Link filtering logic</p>
    </td>
  </tr>
  <tr>
    <td align="center">
      <h3>🧩 Pratiksha</h3>
      <p><b>NLP Engineer</b></p>
      <p>Entity extraction logic<br>Pattern matching rules<br>AI model integration</p>
    </td>
    <td align="center">
      <h3>💻 Priyanshu Gautam</h3>
      <p><b>Frontend Developer</b></p>
      <p>React UI/UX design<br>Component development<br>API integration</p>
    </td>
  </tr>
</table>

---

## 🐛 Troubleshooting

### Backend won't start
- Ensure Python 3.11+ is installed: `python --version`
- Activate virtual environment: `.venv\Scripts\Activate.ps1`
- Install dependencies: `pip install -r requirements.txt`
- Download spaCy model: `python -m spacy download en_core_web_sm`

### Frontend won't start
- Ensure Node.js 18+ is installed: `node --version`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check if port 8080 is available

### Crawl timeout or no results
- Reduce `max_pages` and `max_depth` in Crawl Settings
- Try a simpler domain first (e.g., example.com)
- Check backend logs for errors

### No entities extracted
- Ensure keywords are relevant to the target domain
- Try broader keywords or remove keywords entirely
- Check if the crawled pages contain actual content (not just navigation)

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!  
Feel free to check the [issues page](https://github.com/PrakarshKaushik11/Extractify-The-Coding-Penguins-Deviathon-2025/issues).

---

## 📝 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

You're free to use, modify, and distribute this project with proper attribution.

---

## 💙 Acknowledgements

- Built with ❤️ by **The Coding Penguins** for **Deviathon 2025**
- Powered by **FastAPI**, **spaCy**, **React**, and **Tailwind CSS**
- Special thanks to:
  - Our mentors and organizers at Deviathon 2025
  - The open-source community for amazing tools
  - All judges and supporters of this project

---

## 📧 Contact

For questions, suggestions, or collaboration opportunities:

- **GitHub:** [PrakarshKaushik11](https://github.com/PrakarshKaushik11)
- **LinkedIn:** [Prakarsh Kaushik](https://www.linkedin.com/in/prakarsh-kaushik/)
- **Project Repository:** [Extractify-The-Coding-Penguins-Deviathon-2025](https://github.com/PrakarshKaushik11/Extractify-The-Coding-Penguins-Deviathon-2025)

---

<div align="center">
  <p><b>Made with 🐧 by The Coding Penguins</b></p>
  <p>⭐ Star this repo if you find it helpful!</p>
</div>


