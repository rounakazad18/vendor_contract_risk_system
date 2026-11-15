# Multi-Agent Vendor Contract Risk Review System

A modular, production-oriented **Manager-Worker Multi-Agent System** for analyzing vendor contracts (`.pdf`, `.docx`, `.txt`) against internal company legal, security, and commercial playbooks.

---

## 👥 Authors / Project Credits
- **Group 2:** Gursirat Singh (12326116) & Rounak Azad (12326217)
- **Target Outcome:** CO3 & CO4

---

## 🏗️ System Architecture & Workflow

The system utilizes a 5-agent sequential pipeline coordinated by an asynchronous manager with thread-safe shared memory:

```
Contract Document (.pdf / .docx / .txt)
                    │
                    ▼
   [1] ClauseSplitterAgent      ──> Segments contract into structured clauses & subclauses
                    │
                    ▼
   [2] PlaybookRetrievalAgent   ──> Hybrid RAG semantic retrieval over internal company playbooks
                    │
                    ▼
   [3] RiskScorerAgent          ──> Evaluates policy violations & assigns 0–100 risk score
                    │
                    ▼
   [4] RedlineDrafterAgent      ──> Drafts playbook-aligned redlines (ADD / MODIFY / REMOVE)
                    │
                    ▼
   [5] ReviewManagerAgent       ──> Validates citations, trace logs & compiles final audit report
                    │
                    ▼
      Final Output: Interactive Streamlit UI / PDF / HTML / JSON Reports
```

### Module Breakdown
- **`schemas.py`**: Structured dataclasses (`ClauseRecord`, `PlaybookChunk`, `PlaybookReference`, `DiffOperation`, `ContractReviewReport`, `AgentExecutionTrace`) for typed inter-agent communication.
- **`shared_memory.py`**: Thread-safe and async-safe `SharedClauseTable` with SHA-256 normalized text deduplication and strict state-transition validation.
- **`vector_store.py`**: Hybrid RAG `PlaybookVectorStore` combining TF-IDF unigram/bigram features with 12 legal domain concept clusters and cosine similarity retrieval across multiple playbook documents.
- **`agents/clause_splitter.py` (`ClauseSplitterAgent`)**: Extracts contract text from `.pdf`, `.docx`, and `.txt` files, segments numbered or unnumbered clauses while preserving subclauses, and populates the `SharedClauseTable`.
- **`agents/playbook_retrieval.py` (`PlaybookRetrievalAgent`)**: Runs RAG semantic retrieval per clause, maps governing company policy rules with exact section references, and explicitly flags missing playbook references.
- **`agents/risk_scorer.py` (`RiskScorerAgent`)**: Evaluates each clause on a 0–100 severity scale (`Critical`, `High`, `Medium`, `Low`, `No Risk`), detailing policy violations, missing protections, ambiguous phrasing, and unfavorable obligations.
- **`agents/redline_drafter.py` (`RedlineDrafterAgent`)**: Drafts playbook-grounded replacement wording, structured `REMOVE` / `MODIFY` / `ADD` diff operations, and negotiation fallback rationales for every flagged clause.
- **`agents/review_manager.py` (`ReviewManagerAgent`)**: Central orchestrator managing execution order, controlled asynchronous concurrency (`asyncio.Semaphore`), output validation, and report compilation.
- **`report_generator.py`**: Generates publication-ready HTML/PDF contract review reports and structured JSON exports.
- **`frontend_app.py`**: Interactive Streamlit web UI with side-by-side redline comparison, risk distribution charts, ground-truth benchmarks, and 1-click PDF download.
- **`evaluate_10_clauses.py`**: Ground-truth benchmark evaluator comparing human legal labels against multi-agent predictions.
- **`tests/test_system.py`**: Unit and integration test suite covering all 10 validation dimensions (including PDF, DOCX, TXT, unnumbered contracts, deduplication, and malformed input handling).

---

## 🚀 Quick Start Guide

### 1. Installation

Clone or extract the repository and install the dependencies:

```bash
# Optional: create & activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate       # On macOS / Linux
# .venv\Scripts\activate       # On Windows

# Install required dependencies
pip install -r requirements.txt
```

---

### 2. Launching the Web UI (Streamlit Frontend)

#### macOS / Linux:
```bash
./launch_frontend.sh
```
*Or manually:*
```bash
streamlit run frontend_app.py
```

#### Windows:
Double-click `launch_frontend.bat` or run:
```cmd
launch_frontend.bat
```

Once running, open your browser at **`http://localhost:8501`**.

---

### 3. Running via Command Line (CLI)

To run the end-to-end pipeline directly on the sample contract and generate `report.html` and `report.json`:

```bash
python3 main.py
```

To view the generated HTML report:
```bash
open report.html      # On macOS
# start report.html   # On Windows
```

---

### 4. Running Tests & Benchmarks

```bash
# Run unit & integration test suite
python3 -m unittest discover -s tests -p "test_*.py" -v

# Run the 10-clause ground-truth evaluation benchmark
python3 evaluate_10_clauses.py


./launch_frontend.sh
```
