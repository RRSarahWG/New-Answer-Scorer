# 🏛️ Offline Intelligent Sinhala Open-Ended Answer Scorer

### Anuradhapura Period History — NLP Individual Assignment 02

> **Module:** 40_CS4032 Natural Language Processing  
> **Scope:** Ancient Sri Lanka — Anuradhapura Period (4th century BCE – 11th century CE)

An offline, CPU-compatible intelligent answer scoring system for open-ended Sinhala-language history questions. The system uses **RAG (Retrieval-Augmented Generation)**, an **OWL Ontology**, and a **multi-agent pipeline** powered by a Sinhala-fine-tuned LLM via OLLAMA to evaluate student answers and provide criterion-based scoring with constructive Sinhala feedback.

---

## ✨ Features

- **Full Sinhala UI** — All questions, labels, feedback, and scoring output in Sinhala
- **5 History Questions** — Covering irrigation, Buddhism, rulers, administration, and art/architecture
- **Criterion-Based Scoring** — Each question scored across 5 criteria (total: 20 marks)
- **RAG Pipeline** — FAISS + multilingual sentence-transformers for evidence retrieval
- **OWL Ontology** — rdflib-based knowledge graph with Sinhala labels
- **Multi-Agent Architecture** — 4 specialized agents (Retrieval, Ontology, Scoring, Explanation)
- **100% Offline** — No internet required during scoring

---

## 📁 Project Structure

```
project/
├── app.py                              # Streamlit UI (main entry point)
├── agents/
│   ├── retrieval_agent.py              # RAG retrieval agent
│   ├── ontology_agent.py               # Ontology concept extraction agent
│   ├── scoring_agent.py                # LLM-based scoring agent
│   └── explanation_agent.py            # Sinhala explanation generator
├── rag/
│   ├── knowledge_base.py              # Text chunking logic
│   └── vectorstore.py                 # FAISS index builder & retriever
├── ontology/
│   └── anuradhapura_ontology.py       # OWL ontology (rdflib)
├── data/
│   └── anuradhapura_knowledge.txt     # Sinhala knowledge base
├── questions/
│   └── questions.py                   # 5 questions + marking guides
├── requirements.txt                   # Python dependencies
├── NLP_Assignment_02_Report.md        # Academic report
└── README.md                          # This file
```

---

## 🛠️ Prerequisites

| Requirement | Details |
|-------------|---------|
| **Python** | 3.8 or higher |
| **OLLAMA** | Installed and running ([ollama.com](https://ollama.com)) |
| **Model** | `Tharusha_Dilhara_Jayadeera/singemma:latest` |
| **Hardware** | CPU only (Intel Core i7 8th Gen or equivalent recommended) |

---

## 🚀 Setup & Installation

### 1. Clone or download the project

```bash
cd "E:\KDU\4th year 1st sem\NLP\New Answer Scorer"
```

### 2. Create a virtual environment

```bash
python -m venv venv
.\venv\Scripts\activate       # Windows
# source venv/bin/activate    # Linux/Mac
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and start OLLAMA

Download from [ollama.com](https://ollama.com), then:

```bash
ollama pull Tharusha_Dilhara_Jayadeera/singemma:latest
ollama serve
```

> If you see `bind: Only one usage of each socket address`, OLLAMA is already running — that's fine.

### 5. Run the application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## 📖 How to Use

1. **Select a question** from the dropdown (all in Sinhala)
2. **Read the question** displayed in the blue box
3. **Write your answer in Sinhala** in the text area
4. Click **"පිළිතුර ඇගයීම් කරන්න"** (Score My Answer)
5. Wait ~2–3 minutes for CPU inference
6. Review your **score, criteria breakdown, explanation, and evidence**

---

## 🏗️ Architecture

```
Student Answer (Sinhala)
        │
        ▼
┌─────────────────┐     ┌──────────────────┐
│ Retrieval Agent │     │  Ontology Agent   │
│ FAISS + MiniLM  │     │  rdflib OWL Graph │
│ → Top 3 chunks  │     │  → Sinhala facts  │
└────────┬────────┘     └────────┬─────────┘
         │                       │
         ▼                       ▼
    ┌────────────────────────────────┐
    │        Scoring Agent           │
    │  OLLAMA (SinGemma) + Regex     │
    │  → Per-criterion scores        │
    └───────────────┬────────────────┘
                    ▼
    ┌────────────────────────────────┐
    │      Explanation Agent         │
    │  OLLAMA → Sinhala feedback     │
    └───────────────┬────────────────┘
                    ▼
          Streamlit Results UI
```

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web UI framework |
| `sentence-transformers` | Multilingual embeddings (MiniLM-L12-v2) |
| `faiss-cpu` | Vector similarity search |
| `rdflib` | OWL ontology (RDF/RDFS/OWL) |
| `requests` | OLLAMA API communication |
| `numpy` | Numerical operations |

---

## 📝 Questions Covered

| # | Topic (Sinhala) | Focus Area |
|---|-----------------|------------|
| 1 | වාරිමාර්ග පද්ධති සහ ජලජ ශිෂ්ටාචාරය | Irrigation Systems |
| 2 | බුද්ධාගමය ශ්‍රී ලංකාවට හඳුන්වාදීම | Introduction of Buddhism |
| 3 | ප්‍රකට රජවරුන්: දේවානම්පියතිස්ස සහ දුටුගැමුණු | Notable Rulers |
| 4 | අනුරාධපුර රාජධානියේ පරිපාලන ක්‍රමය | Administrative System |
| 5 | කලාව, ගෘහ නිර්මාණ ශිල්පය සහ සංස්කෘතික ජයග්‍රහණ | Art & Architecture |

Each question carries **20 marks** distributed across **5 criteria**.

---

## ⚡ Performance Notes

- **Scoring time:** ~2–3 minutes per answer on CPU
- **First run:** Additional ~1–2 minutes for FAISS index building and model loading
- **Subsequent runs:** FAISS index loads from disk (`faiss_index.bin`)
- **Embedding model:** Cached in `./model_cache/` after first download

---

## 🔒 Offline Operation

All components run locally after initial setup:

- ✅ OLLAMA + SinGemma model — `localhost:11434`
- ✅ Sentence-transformers — cached in `./model_cache/`
- ✅ FAISS index — saved as `faiss_index.bin`
- ✅ Ontology — pure Python (rdflib)
- ✅ Knowledge base — local `.txt` file
- ✅ Streamlit — `localhost:8501`

**No internet calls during execution.**

---

## 📄 License

This project was developed for academic purposes as part of the NLP Individual Assignment 02.
