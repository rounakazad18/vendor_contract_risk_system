# Q2: Contract Clause Risk Review System (Group 2 — CO3 & CO4, 30 Marks)

- **Group Members**: Gursirat Singh (`12326116`) & Rounak Azad (`12326217`)
- **Architecture**: Manager-Worker Multi-Agent System with Semantic Kernel (`@kernel_function`) tool plugins, RAG `PlaybookVectorStore`, `SharedClauseTable`, `NegotiationHistoryMemory`, and a dedicated Web Frontend (`frontend/`).

## Project Structure

```text
vendor_contract_risk_system/
├── frontend/                        # Proper Web Frontend (HTML5 + CSS3 + ES6 JS + Chart.js)
│   ├── index.html                   # Main enterprise application shell
│   ├── css/
│   │   └── styles.css               # Custom enterprise stylesheet & print styles
│   └── js/
│       └── app.js                   # Frontend state, REST API client, PDF upload & redline studio
├── agents/                          # 5 Separate Specialist AI Agent Modules (Unchanged Backend)
│   ├── clause_splitter.py           # Agent 1: PDF/DOCX/TXT extraction & clause segmentation
│   ├── playbook_retrieval.py        # Agent 2: Hybrid TF-IDF + Legal Concept RAG retrieval
│   ├── risk_scorer.py               # Agent 3: @kernel_function 0–100 rules & severity scorer
│   ├── redline_drafter.py           # Agent 4: Playbook redline drafter + negotiation memory
│   └── review_manager.py            # Agent 5: Central Manager-Worker orchestrator
├── data/
│   └── sample_data.py               # 3 Internal Company Playbooks & PDF/DOCX/TXT sample generator
├── tests/
│   └── test_system.py               # 10 Unit & Integration Test Suites
├── schemas.py                       # Typed dataclasses & enums for inter-agent communication
├── shared_memory.py                 # Thread/Async-safe SharedClauseTable with SHA-256 deduplication
├── vector_store.py                  # RAG PlaybookVectorStore
├── framework_adapter.py             # Semantic Kernel @kernel_function plugin adapter
├── negotiation_memory.py            # Repeat Counterparty Negotiation-History Memory
├── evaluate_10_clauses.py           # CA2 10-Clause Human vs. System Agreement Benchmark (100%)
├── report_generator.py              # Print-ready HTML/PDF report builder
├── main.py                          # CLI pipeline runner
├── server.py                        # Full-Stack REST API & Static Frontend Server (Port 8050)
└── frontend_app.py                  # Alias launcher for server.py
```

## Quick Start (Windows / macOS / Linux — No Streamlit Needed)

1. **Install the 3 backend libraries** (inside your `.venv`):
   ```cmd
   python -m pip install numpy python-docx pdfplumber
   ```
2. **Launch the Proper Web Frontend & REST API Server**:
   ```cmd
   python server.py
   ```
   *(Or `python frontend_app.py` — both automatically open `http://127.0.0.1:8050` in your browser! You can also double-click `frontend/index.html` directly.)*
3. **Run the CA2 10-Clause Agreement Benchmark & Test Suite**:
   ```cmd
   python evaluate_10_clauses.py
   python tests\test_system.py
   ```
