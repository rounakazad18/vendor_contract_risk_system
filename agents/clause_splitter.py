"""
Agent 1: Clause Splitter Agent
Responsibilities:
- Extract text from uploaded vendor contracts (PDF, DOCX, or TXT).
- Break the contract into individual, numbered clauses.
- Preserve clause numbering, headings, and subclauses.
- Assign a unique ID to every clause.
- Store extracted clauses in the SharedClauseTable.
- Handle poorly formatted or unnumbered contracts gracefully.
"""

from __future__ import annotations
import logging
import os
import re
from typing import List, Tuple
import docx
import pdfplumber
from schemas import ClauseRecord, ProcessingStatus
from shared_memory import SharedClauseTable

logger = logging.getLogger(__name__)


class ClauseSplitterAgent:
    """
    Agent 1: Extracts contract text from PDF, DOCX, or TXT files, parses numbered
    or unnumbered clauses (preserving subclauses), assigns unique Clause IDs, and
    populates the SharedClauseTable.
    """

    AGENT_NAME = "ClauseSplitterAgent"

    UNNUMBERED_HEADING_KEYWORDS = [
        "scope of services",
        "deliverables",
        "term and renewal",
        "term & termination",
        "termination",
        "fees and payment",
        "payment terms",
        "invoicing",
        "intellectual property",
        "work product",
        "indemnification",
        "indemnity",
        "limitation of liability",
        "liability",
        "confidentiality",
        "non-disclosure",
        "data privacy",
        "data protection",
        "security incident",
        "audit rights",
        "regulatory compliance",
        "subcontracting",
        "subprocessors",
        "governing law",
        "dispute resolution",
        "force majeure",
        "warranties",
    ]

    def extract_text_from_file(self, file_path: str) -> str:
        """
        Extracts raw text from a PDF, DOCX, or TXT vendor contract file.
        Raises ValueError on unsupported or corrupted/empty files.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Contract file not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        extracted_text = ""

        if ext in (".txt", ".md"):
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                extracted_text = f.read()

        elif ext == ".docx":
            try:
                doc = docx.Document(file_path)
                blocks: List[str] = []
                for p in doc.paragraphs:
                    if p.text and p.text.strip():
                        blocks.append(p.text.strip())
                for table in doc.tables:
                    for row in table.rows:
                        row_cells = [c.text.strip() for c in row.cells if c.text.strip()]
                        if row_cells:
                            blocks.append(" | ".join(row_cells))
                extracted_text = "\n\n".join(blocks)
            except Exception as exc:
                raise ValueError(f"Failed to read DOCX contract '{file_path}': {exc}") from exc

        elif ext == ".pdf":
            try:
                pages_text: List[str] = []
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        t = page.extract_text()
                        if t and t.strip():
                            pages_text.append(t.strip())
                extracted_text = "\n\n".join(pages_text)
            except Exception as exc:
                raise ValueError(f"Failed to read PDF contract '{file_path}': {exc}") from exc
        else:
            raise ValueError(
                f"Unsupported contract format '{ext}'. Supported formats: .pdf, .docx, .txt"
            )

        if not extracted_text or not extracted_text.strip():
            raise ValueError(f"Extracted text from '{file_path}' is empty.")

        return extracted_text

    def split_text_into_clauses(
        self, raw_text: str, shared_table: SharedClauseTable, contract_prefix: str = "CL"
    ) -> List[ClauseRecord]:
        """
        Splits raw contract text into structured ClauseRecord objects, handles both
        well-structured numbered clauses and poorly formatted/unnumbered contracts,
        preserves subclauses, and registers them in SharedClauseTable.
        """
        if not raw_text or not raw_text.strip():
            raise ValueError("Cannot split empty contract text.")

        normalized = re.sub(r"\r\n?", "\n", raw_text).strip()
        parsed_tuples = self._split_numbered_clauses(normalized)

        if len(parsed_tuples) < 2:
            logger.info(
                "Contract lacks standard numbering; invoking unnumbered/poorly-formatted clause segmentation."
            )
            parsed_tuples = self._split_unnumbered_clauses(normalized)

        registered_records: List[ClauseRecord] = []
        seq = 1
        for cl_num, heading, body_text, subclauses in parsed_tuples:
            clean_body = body_text.strip()
            if len(clean_body) < 15:
                continue

            clause_id = f"{contract_prefix}-{seq:03d}"
            record = ClauseRecord(
                clause_id=clause_id,
                clause_number=str(cl_num) if cl_num else str(seq),
                clause_heading=heading.strip(),
                original_text=clean_body,
                subclauses=subclauses,
                processing_status=ProcessingStatus.EXTRACTED,
            )

            if shared_table.register_clause(record):
                registered_records.append(record)
                seq += 1

        return registered_records

    def _split_numbered_clauses(
        self, text: str
    ) -> List[Tuple[str, str, str, List[str]]]:
        """
        Identifies top-level numbered clauses while keeping subclauses (1.1, 1.2, (a), (b))
        nested inside their parent clause.
        """
        pattern = re.compile(
            r"(?m)^(?:(?:SECTION|ARTICLE|CLAUSE)\s+)?(\d{1,2})[\.\:\)]\s+([A-Z][A-Za-z0-9\s\,\&\-\/\(\)\']{2,75}?)(?:\.\s+|\n)"
        )
        matches = list(pattern.finditer(text))
        if len(matches) < 2:
            return []

        clauses: List[Tuple[str, str, str, List[str]]] = []
        for i, match in enumerate(matches):
            cl_num = match.group(1).strip()
            heading = match.group(2).strip().rstrip(".:-")
            start_idx = match.start()
            end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            full_block = text[start_idx:end_idx].strip()

            subclauses = self._extract_subclauses(full_block, cl_num)
            clauses.append((cl_num, heading, full_block, subclauses))

        return clauses

    def _extract_subclauses(self, block_text: str, parent_num: str) -> List[str]:
        sub_pattern = re.compile(
            rf"(?m)^\s*(\({parent_num}\)|{re.escape(parent_num)}\.\d+|\([a-z]\)|\([ivx]+\))\s+(.+)$"
        )
        found: List[str] = []
        for m in sub_pattern.finditer(block_text):
            marker = m.group(1).strip()
            content = m.group(2).strip()
            found.append(f"{marker} {content}")
        return found

    def _split_unnumbered_clauses(
        self, text: str
    ) -> List[Tuple[str, str, str, List[str]]]:
        """
        Segments poorly formatted or unnumbered contracts by paragraph breaks or inline
        all-caps / keyword headings and assigns synthetic sequential numbers.
        """
        raw_paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", text) if p.strip()]
        if len(raw_paragraphs) == 1:
            raw_paragraphs = [
                p.strip()
                for p in re.split(r"(?=\b[A-Z]{4,}(?:\s+[A-Z]{3,})+\s*[:\-])", text)
                if p.strip()
            ]
            if len(raw_paragraphs) == 1:
                sentences = re.split(r"(?<=[\.\!\?])\s+(?=[A-Z])", text)
                raw_paragraphs = [
                    " ".join(sentences[i : i + 3]) for i in range(0, len(sentences), 3)
                ]

        results: List[Tuple[str, str, str, List[str]]] = []
        seq = 1
        verb_re = re.compile(
            r"\b(shall|will|may|must|agrees|agree|liable|warrants|warrant)\b",
            re.IGNORECASE,
        )
        for para in raw_paragraphs:
            has_legal_verb = bool(verb_re.search(para))
            if (len(para) < 65 or "." not in para) and not has_legal_verb:
                continue

            heading = self._infer_heading(para, seq)
            subclauses = self._extract_subclauses(para, str(seq))
            results.append((str(seq), heading, para, subclauses))
            seq += 1

        return results

    def _infer_heading(self, paragraph: str, seq: int) -> str:
        first_line = paragraph.splitlines()[0].strip()
        colon_match = re.match(r"^([A-Za-z0-9\s\&\-\/]{3,55})[\:\-—]\s+", first_line)
        if colon_match:
            return colon_match.group(1).strip().title()

        lower_p = paragraph.lower()
        for kw in self.UNNUMBERED_HEADING_KEYWORDS:
            if kw in lower_p:
                return kw.title()

        words = re.findall(r"[A-Za-z]+", first_line)[:5]
        return " ".join(words).title() if words else f"Unnumbered Provision {seq}"
