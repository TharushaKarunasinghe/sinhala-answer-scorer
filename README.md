<div align="center">

# 📜 Sinhala Answer Scorer
### Offline Intelligent Sinhala Open-Ended Answer Scoring System
#### Colonial Sri Lanka History (Portuguese → Dutch → British)

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.45.1-red?logo=streamlit)](https://streamlit.io/)
[![OLLAMA](https://img.shields.io/badge/OLLAMA-0.24.0-black?logo=ollama)](https://ollama.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-1.0.9-orange)](https://www.trychroma.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

> A fully **offline**, agent-based AI system that scores Sinhala open-ended history answers using RAG, OWL Ontology, and local LLM inference via OLLAMA. All content — questions, answers, scoring, explanations — is in **Sinhala Unicode**.

[Features](#-features) • [Architecture](#-architecture) • [Tech Stack](#-tech-stack) • [Setup](#-setup) • [Usage](#-usage) • [Agents](#-agent-architecture) • [File Structure](#-file-structure)

</div>

---

## ✨ Features

- 🔒 **Fully Offline** — zero internet required at runtime; all inference runs locally via OLLAMA
- 🇱🇰 **Sinhala Unicode throughout** — questions, marking guides, scoring prompts, explanations, and UI all in Sinhala
- 🤖 **Four-Agent Architecture** — Retrieval → Ontology → Scoring → Explanation, each with a single clear responsibility
- 🔍 **RAG Pipeline** — ChromaDB vector store with `nomic-embed-text` embeddings retrieves the most relevant historical context before scoring
- 🧠 **OWL Ontology** — 12 classes and 48 individuals covering Colonial Sri Lanka concepts, used to verify factual accuracy and detect era mismatches
- 📊 **Explainable Scoring** — per-criterion mark breakdown (out of 20) with Sinhala evidence-based justification
- 🖥️ **Streamlit UI** — clean, fully Sinhala interface for question selection, answer entry, and result display

---

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Streamlit UI                        │
│  Select Question │ Enter Sinhala Answer │ View Results  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                  Agent Orchestrator                     │
│         Routes tasks · Aggregates outputs               │
└──┬─────────────┬──────────────┬─────────────────────────┘
   │             │              │
   ▼             ▼              ▼
┌──────────┐ ┌──────────┐ ┌──────────────────────────────┐
│Retrieval │ │Ontology  │ │      Scoring Agent           │
│  Agent   │ │  Agent   │ │ (Scoring + Explanation in    │
│          │ │          │ │  one OLLAMA call)            │
│ChromaDB  │ │OWL/RDF   │ └──────────────────────────────┘
│nomic-    │ │owlready2 │
│embed-text│ │era check │
└────┬─────┘ └────┬─────┘
     │             │
     ▼             ▼
┌─────────────────────────────────────────────────────────┐
│              OLLAMA — Local LLM Inference               │
│   SinGemma (Sinhala fine-tuned) · nomic-embed-text      │
└─────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│                  Local Knowledge Base                   │
│   portuguese_era.txt · dutch_era.txt · british_era.txt  │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. User selects a question and enters a Sinhala answer in the Streamlit UI
2. **Orchestrator** receives the request and triggers the agent pipeline
3. **Retrieval Agent** embeds the question + answer using `nomic-embed-text` and fetches the top-4 most relevant chunks from ChromaDB
4. **Ontology Agent** scans the answer for known Colonial Sri Lanka concepts (battles, treaties, persons, reforms, etc.) using a keyword → OWL individual map; flags era mismatches if the student references wrong-era events
5. **Scoring Agent** constructs a single structured prompt combining the question, marking criteria, retrieved context, ontology matches, and era warnings — sends it to SinGemma via OLLAMA and parses the JSON response containing per-criterion scores and an overall explanation
6. Results are rendered in the Streamlit UI with a score breakdown, progress bars, Sinhala explanation, and expandable evidence panels

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|---|---|---|
| LLM Inference | [OLLAMA](https://ollama.com/) + `SinGemma` | Local Sinhala language scoring |
| Embeddings | `nomic-embed-text` via OLLAMA | Offline vector embeddings for RAG |
| Vector Store | [ChromaDB](https://www.trychroma.com/) | Persistent local similarity search |
| RAG Framework | [LangChain](https://www.langchain.com/) + `langchain-ollama` | Document loading, splitting, retrieval |
| Ontology | [owlready2](https://owlready2.readthedocs.io/) + OWL/RDF | Knowledge graph for Colonial SL concepts |
| UI | [Streamlit](https://streamlit.io/) | Interactive Sinhala web interface |
| Language | Python 3.12 | Core implementation |

### OLLAMA Models Used

| Model | Size | Role |
|---|---|---|
| `Tharusha_Dilhara_Jayadeera/singemma:latest` | 2.5 GB | Sinhala scoring + explanation |
| `nomic-embed-text:latest` | 274 MB | Document + query embeddings |

---

## ⚙️ Setup

### Prerequisites

- Python 3.12+
- [OLLAMA](https://ollama.com/download) installed and running
- Git

### 1. Clone the repository

```bash
git clone https://github.com/TharushaKarunasinghe/sinhala-answer-scorer.git
cd sinhala-answer-scorer
```

### 2. Pull required OLLAMA models

```bash
ollama pull nomic-embed-text
ollama pull Tharusha_Dilhara_Jayadeera/singemma:latest
```

### 3. Create virtual environment and install dependencies

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 4. Build the ChromaDB knowledge base (run once)

```bash
python scripts/ingest_knowledge_base.py
```

This script loads the three knowledge base files from `knowledge_base/`, splits them into chunks, generates embeddings using `nomic-embed-text`, and persists the vector store to `chroma_db/`.

Expected output:
```
📂 Loading knowledge base files...
  ✅ Loaded: british_era.txt
  ✅ Loaded: dutch_era.txt
  ✅ Loaded: portuguese_era.txt
✂️  Splitting into chunks...
  Total chunks: ~45
🔢 Generating embeddings with nomic-embed-text (offline)...
💾 Saving to ChromaDB...
✅ Ingestion complete.
```

### 5. Run the application

```bash
streamlit run app.py --server.fileWatcherType none
```

Open `http://localhost:8501` in your browser.

---

## 🚀 Usage

1. **Select a question** from the dropdown — 5 questions covering Portuguese, Dutch, British, and comparative eras
2. **Type your Sinhala answer** in the text area
3. **Click "ලකුණු ගණනය කරන්න"** (Calculate Score)
4. View your results:
   - Total score out of 20 with grade
   - Per-criterion mark breakdown with Sinhala reasoning
   - Overall comment and detailed explanation
   - Expandable RAG evidence panel (retrieved knowledge base chunks)
   - Expandable ontology concepts panel (matched Colonial SL entities)

---

## 🕵️ Agent Architecture

The system uses four specialised agents coordinated by a central orchestrator. Each agent has a single, well-defined responsibility.

### AgentOrchestrator — `core/orchestrator.py`
The central controller. Initialises all agents at startup, loads the question bank, and runs the full pipeline in sequence for each scoring request. Aggregates all agent outputs into a single result dict returned to the UI.

### RetrievalAgent — `agents/retrieval_agent.py`
Uses `nomic-embed-text` embeddings and ChromaDB to find the top-4 most semantically relevant chunks from the knowledge base given the question and student answer. Formats chunks with era metadata for the scoring prompt. This grounds the LLM in factual historical content rather than relying on parametric memory.

### OntologyAgent — `agents/ontology_agent.py`
Loads `colonial_ontology.owl` (12 OWL classes, 48 named individuals) via `owlready2`. Scans the student answer using a Sinhala keyword → ontology individual mapping to identify mentioned concepts (battles, treaties, persons, reforms, economic systems, etc.). Also runs an **era mismatch check** — if a student answering a Portuguese-era question mentions Dutch-era events, this is flagged as a factual error and passed to the Scoring Agent to penalise.

### ScoringAgent — `agents/scoring_agent.py`
Constructs a structured Sinhala prompt combining all inputs (question, marking criteria, RAG context, ontology matches, era warnings) and sends it to SinGemma via OLLAMA. Parses the JSON response containing per-criterion awarded marks with Sinhala reasoning and an overall explanation. Clamps all marks to their valid range and recalculates the total independently to prevent LLM arithmetic errors.

### ExplanationAgent *(merged into ScoringAgent)*
For performance, the explanation is generated in the same OLLAMA call as scoring, returned as an `explanation` field in the JSON response. This halves the inference time compared to two separate calls.

---

## 📁 File Structure

```
sinhala-answer-scorer/
│
├── knowledge_base/                  # Sinhala historical text files
│   ├── portuguese_era.txt           # Portuguese colonial period (1505–1658)
│   ├── dutch_era.txt                # Dutch colonial period (1658–1796)
│   └── british_era.txt              # British colonial period (1796–1948)
│
├── data/
│   └── questions.json               # 5 Sinhala questions with marking guides
│
├── ontology/
│   └── colonial_ontology.owl        # OWL ontology — 12 classes, 48 individuals
│
├── chroma_db/                       # Auto-generated ChromaDB vector store
│
├── agents/
│   ├── __init__.py
│   ├── retrieval_agent.py           # ChromaDB similarity search
│   ├── ontology_agent.py            # OWL concept detection + era mismatch
│   ├── scoring_agent.py             # LLM scoring + explanation (single call)
│   └── explanation_agent.py         # (merged into scoring_agent)
│
├── core/
│   ├── __init__.py
│   ├── orchestrator.py              # Agent pipeline coordinator
│   └── ollama_client.py             # OLLAMA chat wrapper + JSON parser
│
├── scripts/
│   └── ingest_knowledge_base.py     # One-time ChromaDB ingestion script
│
├── app.py                           # Streamlit UI entry point
├── requirements.txt                 # Python dependencies
├── .gitignore
└── README.md
```

---

## 📋 Questions Covered

| ID | Era | Topic |
|---|---|---|
| Q1 | 🇵🇹 Portuguese | Political and religious impact of Portuguese rule (1505–1658) |
| Q2 | 🇵🇹 Portuguese | Three major battles against Portuguese (Mulleriyawa, Danture, Randeniwela) |
| Q3 | 🇳🇱 Dutch | Economic, legal and social impact of Dutch rule (1658–1796) |
| Q4 | 🇬🇧 British | Plantation economy, railways and infrastructure under British rule (1796–1948) |
| Q5 | ⚖️ Comparative | Comparison of governance styles across all three colonial powers |

Each question is graded out of **20 marks** using 5 structured criteria, with marks clamped and totals independently recalculated.

---

## 🧩 Ontology Coverage

The OWL ontology (`colonial_ontology.owl`) covers 12 classes and 48 named individuals:

| Class | Examples |
|---|---|
| ColonialPower | පෘතුගීසීන්, ලන්දේසීන්, බ්‍රිතාන්‍යයන් |
| Era | PortugueseEra, DutchEra, BritishEra |
| Battle | මුල්ලේරියා සටන, දන්තුරේ සටන, රන්දෙනිවෙල සටන |
| Treaty | වෙස්ටර්වෝල්ඩ් ගිවිසුම, හඟුරන්කෙත ගිවිසුම, උඩරට ගිවිසුම |
| Person | ධර්මපාල, රාජසිංහ, කැප්පෙටිපොල, ජේම්ස් ටේලර් |
| Reform | කෝල්බෲක්-කැමරන්, ඩොනමෝර්, සෝල්බරි ව්‍යවස්ථාව |
| EconomicSystem | VOC, වතු ආර්ථිකය, කුළුබඩු ඒකාධිකාරය |
| LegalSystem | රෝම-ලන්දේසි නීතිය, බ්‍රිතාන්‍ය පොදු නීතිය |
| Infrastructure | දුම්රිය ක්‍රමය, ගාල්ල ලන්දේසි බලකොටුව |
| SocialGroup | බර්ගර් ප්‍රජාව, ඉන්දියානු ශ්‍රමිකයන් |

---

## 👤 Author

**Tharusha Karunasinghe**
- GitHub: [@TharushaKarunasinghe](https://github.com/TharushaKarunasinghe)
- LinkedIn: [linkedin.com/in/tharusha-kalhara]([https://linkedin.com/in/tharusha-kalhara](https://www.linkedin.com/in/tharusha-kalhara-06a20324a/))

---

<div align="center">
Built with ❤️ for Sinhala AI · Runs fully offline · No cloud required
</div>
