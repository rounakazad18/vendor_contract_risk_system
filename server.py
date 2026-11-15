"""
REST API & Static Frontend Web Server (`server.py` / `frontend_app.py`)
Group 2: Gursirat Singh (12326116) & Rounak Azad (12326217) — Q2 CA2 (30 Marks)

Serves the proper multi-file frontend (`frontend/index.html`, `frontend/css/styles.css`,
`frontend/js/app.js`) and connects it via REST API endpoints to the existing Python
multi-agent backend without modifying any backend agent or helper modules:
- GET  /                    -> Serves `frontend/index.html`
- GET  /css/styles.css      -> Serves `frontend/css/styles.css`
- GET  /js/app.js           -> Serves `frontend/js/app.js`
- GET  /api/initial         -> Runs default benchmark contract & 10-clause evaluation
- POST /api/analyze         -> Accepts uploaded PDF/DOCX/TXT contract, runs all 5 agents, returns report
- POST /api/download_pdf    -> Generates and returns binary `.pdf` Contract Review Report

Launch with:
    python server.py
"""

from __future__ import annotations
import asyncio
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import mimetypes
import os
import tempfile
import webbrowser
from typing import Dict, Any, List

from agents import ReviewManagerAgent
from data.sample_data import (
    populate_default_vector_store,
    generate_sample_contract_files,
    _write_text_pdf,
)
from negotiation_memory import populate_default_negotiation_memory
from evaluate_10_clauses import run_10_clause_evaluation


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
SAMPLE_DIR = os.path.join(BASE_DIR, "data", "generated_samples")

VECTOR_STORE = populate_default_vector_store()
NEGOTIATION_MEMORY = populate_default_negotiation_memory()
SAMPLE_FILES = generate_sample_contract_files(SAMPLE_DIR)


def build_pdf_report_bytes(report_dict: Dict[str, Any]) -> bytes:
    es = report_dict["executive_summary"]
    fr = report_dict["final_recommendations"]
    lines: List[str] = [
        "=========================================================================================",
        "Q2: CONTRACT CLAUSE RISK REVIEW SYSTEM — OFFICIAL REVIEW REPORT (CO3 & CO4, 30 MARKS)",
        "Group 2 Members: Gursirat Singh (12326116) & Rounak Azad (12326217)",
        "=========================================================================================",
        f"Contract File   : {report_dict.get('contract_filename', 'Uploaded_Contract.pdf')}",
        f"Report ID       : {report_dict.get('report_id', 'RPT-2026')}   |   Generated: {report_dict.get('generated_at', '')}",
        f"Composite Score : {es['overall_contract_risk_score']}/100 ({es['overall_risk_level']})",
        f"Approval Status : {fr['approval_recommendation']}",
        "",
        "1. EXECUTIVE SUMMARY",
        "-----------------------------------------------------------------------------------------",
        es["overall_assessment_narrative"],
        f"Total Clauses: {es['total_clauses_analyzed']} | Flagged: {es['flagged_clauses_count']} "
        f"(Critical: {es['critical_count']}, High: {es['high_count']}, Medium: {es['medium_count']}, "
        f"Low: {es['low_count']}, No Risk: {es['no_risk_count']})",
        "",
        "2. RISK-RANKED CLAUSE ANALYSIS & SUGGESTED PLAYBOOK REDLINES",
        "-----------------------------------------------------------------------------------------",
    ]

    for cl in report_dict.get("risk_ranked_clauses", []):
        refs = cl.get("retrieved_playbook_references", [])
        ref_str = refs[0]["section_ref"] + " (" + refs[0]["heading"] + ")" if refs else "No Direct Match"
        lines.append(
            f"CLAUSE {cl['clause_number']}: {cl['clause_heading']} [{cl['clause_id']}]"
        )
        lines.append(
            f"Risk Score: {cl['risk_score']}/100 | Severity: {cl['risk_severity']} | Playbook Ref: {ref_str}"
        )
        lines.append(f"Original Wording: {cl['original_text']}")
        lines.append(f"Risk Assessment : {cl['risk_explanation']}")
        if cl.get("is_flagged"):
            lines.append(f"Suggested Redline: {cl['suggested_replacement_wording']}")
            lines.append(f"Redline Rationale: {cl['redline_rationale']}")
        lines.append("-" * 89)

    lines.append("")
    lines.append("3. FINAL APPROVAL RECOMMENDATION & NEGOTIATION PRIORITIES")
    lines.append("-----------------------------------------------------------------------------------------")
    lines.append(f"Recommendation: {fr['approval_recommendation']} — {fr['approval_justification']}")
    for p in fr.get("recommended_negotiation_priorities", []):
        lines.append(f" * {p}")

    tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp_pdf.close()
    try:
        _write_text_pdf(tmp_pdf.name, "\n".join(lines))
        with open(tmp_pdf.name, "rb") as f:
            return f.read()
    finally:
        if os.path.exists(tmp_pdf.name):
            os.remove(tmp_pdf.name)


class WebAppRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:
        pass

    def _send_json(self, payload: Dict[str, Any], status: int = 200) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _serve_static(self, rel_path: str) -> None:
        full_path = os.path.normpath(os.path.join(FRONTEND_DIR, rel_path))
        if not full_path.startswith(FRONTEND_DIR) or not os.path.isfile(full_path):
            self.send_error(404, "File Not Found")
            return
        mime, _ = mimetypes.guess_type(full_path)
        if full_path.endswith(".js"):
            mime = "application/javascript"
        mime = mime or "application/octet-stream"
        with open(full_path, "rb") as f:
            data = f.read()
        self.send_response(200)
        content_type = f"{mime}; charset=utf-8" if (mime.startswith("text/") or mime == "application/javascript") else mime
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        clean_path = self.path.split("?")[0]
        if clean_path in ("/", "/index.html"):
            self._serve_static("index.html")
            return
        if clean_path.startswith(("/css/", "/js/")):
            self._serve_static(clean_path.lstrip("/"))
            return

        if clean_path.startswith("/api/initial"):
            manager = ReviewManagerAgent(
                vector_store=VECTOR_STORE,
                negotiation_memory=NEGOTIATION_MEMORY,
                counterparty_name="ApexCloud Infrastructure Inc.",
            )
            rpt = asyncio.run(
                manager.analyze_contract_file(SAMPLE_FILES["pdf"], contract_prefix="APEX")
            )
            eval_summary = asyncio.run(run_10_clause_evaluation())
            self._send_json(
                {
                    "report": rpt.to_dict(),
                    "evaluation": eval_summary.to_dict(),
                }
            )
            return

        self.send_error(404, "Not Found")

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body_bytes = self.rfile.read(length)
        data = json.loads(body_bytes.decode("utf-8"))

        if self.path.startswith("/api/analyze"):
            filename = data.get("filename", "Uploaded_Contract.pdf")
            counterparty = data.get("counterparty", "ApexCloud Infrastructure Inc.")
            file_b64 = data.get("file_base64", "")
            ext = os.path.splitext(filename)[1].lower() or ".txt"

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
            try:
                tmp.write(base64.b64decode(file_b64))
                tmp.close()
                manager = ReviewManagerAgent(
                    vector_store=VECTOR_STORE,
                    negotiation_memory=NEGOTIATION_MEMORY,
                    counterparty_name=counterparty,
                )
                rpt = asyncio.run(
                    manager.analyze_contract_file(tmp.name, contract_prefix="UPL")
                )
                rpt.contract_filename = filename
                self._send_json({"report": rpt.to_dict()})
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=400)
            finally:
                if os.path.exists(tmp.name):
                    os.remove(tmp.name)
            return

        if self.path.startswith("/api/download_pdf"):
            report_dict = data.get("report", {})
            pdf_bytes = build_pdf_report_bytes(report_dict)
            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Length", str(len(pdf_bytes)))
            self.end_headers()
            self.wfile.write(pdf_bytes)
            return

        self.send_error(404, "Not Found")


def run_server(port: int = 8050) -> None:
    server = HTTPServer(("127.0.0.1", port), WebAppRequestHandler)
    url = f"http://127.0.0.1:{port}"
    print("=" * 80)
    print("Q2 CONTRACT CLAUSE RISK REVIEW SYSTEM — PROPER WEB FRONTEND & REST API SERVER")
    print("Group 2: Gursirat Singh (12326116) & Rounak Azad (12326217)")
    print(f"Serving frontend/index.html at: {url}")
    print("Press Ctrl+C to stop the server.")
    print("=" * 80)
    try:
        webbrowser.open(url)
    except Exception:
        pass
    server.serve_forever()


if __name__ == "__main__":
    run_server()
