"""
RAG Vector Database & Embedding Engine for Internal Company Playbooks.
Supports indexing multiple playbook documents, chunking, hybrid lexical + semantic
domain concept embeddings, and cosine similarity search with strict source provenance.
"""

from __future__ import annotations
import math
import re
from collections import Counter
from typing import Dict, List, Tuple
import numpy as np
from schemas import PlaybookChunk, PlaybookReference


# Legal domain concept synsets to give dense semantic concept dimensions alongside TF-IDF n-grams
LEGAL_CONCEPT_CLUSTERS: Dict[str, List[str]] = {
    "CONCEPT_LIABILITY": [
        "liability", "cap", "consequential", "indirect", "punitive", "special",
        "damages", "super-cap", "aggregate", "limitation", "unlimited", "fees paid",
        "preceding twelve", "12 months", "1 month",
    ],
    "CONCEPT_INDEMNITY": [
        "indemnify", "indemnification", "hold harmless", "defend", "third-party",
        "infringement", "claim", "losses", "indemnitee", "indemnitor", "mutual",
    ],
    "CONCEPT_IP_OWNERSHIP": [
        "intellectual property", "work product", "deliverables", "work made for hire",
        "assignment", "assigns", "derivative", "custom", "background ip", "pre-existing",
        "ownership", "patent", "copyright", "trade secret", "title",
    ],
    "CONCEPT_DATA_PRIVACY_AI": [
        "personal data", "gdpr", "ccpa", "dpia", "data breach", "security incident",
        "notification", "hours", "24 hours", "72 hours", "encryption", "ai",
        "machine learning", "foundation model", "training", "telemetry", "anonymized",
    ],
    "CONCEPT_TERM_TERMINATION": [
        "term", "renewal", "auto-renewal", "automatically renew", "notice", "termination",
        "convenience", "cure period", "material breach", "wind-down", "transition",
        "refund", "pro-rata", "lock-in",
    ],
    "CONCEPT_PAYMENT_FEES": [
        "payment", "invoice", "net-15", "net-30", "net-45", "net-60", "late fee",
        "interest", "price increase", "escalation", "cpi", "disputed", "withhold",
        "taxes", "billing",
    ],
    "CONCEPT_GOVERNING_LAW_DISPUTE": [
        "governing law", "jurisdiction", "venue", "arbitration", "courts", "delaware",
        "new york", "cayman", "jury", "attorneys' fees", "prevailing party", "dispute",
    ],
    "CONCEPT_AUDIT_COMPLIANCE": [
        "audit", "soc 2", "iso 27001", "penetration test", "inspection", "records",
        "compliance", "regulatory", "self-attestation", "certifications",
    ],
    "CONCEPT_SUBCONTRACTING": [
        "subcontractor", "subprocessor", "fourth-party", "affiliate", "delegate",
        "prior written consent", "flow-down", "objection",
    ],
    "CONCEPT_CONFIDENTIALITY": [
        "confidential", "non-disclosure", "nda", "proprietary", "receiving party",
        "disclosing party", "standard of care", "compelled disclosure", "return or destroy",
    ],
    "CONCEPT_FORCE_MAJEURE": [
        "force majeure", "act of god", "disaster", "pandemic", "business continuity",
        "disaster recovery", "rto", "rpo", "excused",
    ],
    "CONCEPT_SCOPE_SLA": [
        "scope", "services", "sla", "uptime", "availability", "99.9%", "service credits",
        "support", "maintenance", "affiliates",
    ],
}

STOPWORDS = {
    "the", "and", "for", "that", "this", "with", "from", "shall", "will", "may",
    "any", "all", "are", "was", "were", "been", "have", "has", "had", "not", "but",
    "its", "their", "our", "your", "such", "under", "into", "upon", "other", "than",
    "which", "who", "whom", "whose", "where", "when", "why", "how", "each", "every",
}


class PlaybookVectorStore:
    """
    In-memory Vector Store that chunks internal company playbooks, builds dense
    hybrid embeddings (TF-IDF unigram/bigram features + domain semantic concept features),
    and executes cosine-similarity search with exact source attribution.
    """

    def __init__(self) -> None:
        self.chunks: List[PlaybookChunk] = []
        self.vocab: Dict[str, int] = {}
        self.idf: np.ndarray = np.array([])
        self.embeddings: np.ndarray = np.array([])
        self.indexed_documents: Dict[str, str] = {}  # doc_id -> title

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        cleaned = re.sub(r"[^a-z0-9\-\.%]+", " ", text.lower())
        raw_tokens = [t.strip("-") for t in cleaned.split() if len(t.strip("-")) >= 2]
        unigrams = [t for t in raw_tokens if t not in STOPWORDS]
        bigrams = [f"{unigrams[i]}_{unigrams[i+1]}" for i in range(len(unigrams) - 1)]
        return unigrams + bigrams

    def _compute_concept_activations(self, text: str) -> List[float]:
        lower_text = text.lower()
        activations: List[float] = []
        for _, keywords in sorted(LEGAL_CONCEPT_CLUSTERS.items()):
            hits = sum(1 for kw in keywords if kw in lower_text)
            # Smooth log-scaled concept weight boosted to anchor semantic similarity
            activations.append(math.log1p(hits) * 2.8)
        return activations

    def index_chunks(self, new_chunks: List[PlaybookChunk]) -> int:
        """
        Adds playbook chunks to the vector index and recomputes normalized embeddings.
        """
        existing_ids = {c.chunk_id for c in self.chunks}
        added = 0
        for ch in new_chunks:
            if ch.chunk_id not in existing_ids:
                self.chunks.append(ch)
                existing_ids.add(ch.chunk_id)
                self.indexed_documents[ch.document_id] = ch.document_title
                added += 1

        self._rebuild_matrix()
        return added

    def parse_and_index_markdown_playbook(
        self, document_id: str, document_title: str, markdown_text: str
    ) -> int:
        """
        Chunks a structured Markdown playbook document into PlaybookChunk records
        and indexes them in the vector database.
        """
        sections = re.split(r"(?m)^##\s+", markdown_text)
        parsed_chunks: List[PlaybookChunk] = []

        for idx, sec in enumerate(sections):
            sec = sec.strip()
            if not sec:
                continue
            lines = sec.splitlines()
            header_line = lines[0].strip()
            body_text = "\n".join(lines[1:]).strip()
            if not body_text:
                continue

            # Parse section_ref and heading from e.g. "§4.1 Limitation of Liability & Super-Caps [Category: Liability]"
            cat_match = re.search(r"\[Category:\s*([^\]]+)\]", header_line, re.IGNORECASE)
            category = cat_match.group(1).strip() if cat_match else "General"
            clean_header = re.sub(r"\[Category:[^\]]+\]", "", header_line).strip()

            ref_match = re.match(r"^(§[\d\.]+|Section\s+[\d\.]+)\s*[:\-—]?\s*(.*)$", clean_header)
            if ref_match:
                section_ref = f"{document_id} {ref_match.group(1)}"
                heading = ref_match.group(2).strip() or clean_header
            else:
                section_ref = f"{document_id} §{idx}"
                heading = clean_header

            def _extract_field(label: str) -> str:
                pattern = rf"(?im)^\*\*{label}\*\*:\s*(.+?)(?=\n\*\*[A-Za-z ]+\*\*:|\Z)"
                m = re.search(pattern, body_text, re.DOTALL)
                return m.group(1).strip() if m else ""

            policy_rule = _extract_field("Governing Policy Rule") or body_text[:300]
            mandatory_raw = _extract_field("Mandatory Requirements")
            prohibited_raw = _extract_field("Prohibited Terms")
            fallback = _extract_field("Fallback Position")
            preferred_template = _extract_field("Preferred Replacement Wording")

            mandatory_list = [
                x.strip(" -•*") for x in re.split(r"[;\n]", mandatory_raw) if x.strip(" -•*")
            ]
            prohibited_list = [
                x.strip(" -•*") for x in re.split(r"[;\n]", prohibited_raw) if x.strip(" -•*")
            ]

            chunk = PlaybookChunk(
                chunk_id=f"{document_id}_CHUNK_{idx:02d}",
                document_id=document_id,
                document_title=document_title,
                section_ref=section_ref,
                heading=heading,
                category=category,
                policy_rule=policy_rule,
                mandatory_requirements=mandatory_list,
                prohibited_terms=prohibited_list,
                fallback_position=fallback,
                preferred_wording_template=preferred_template,
                raw_excerpt=body_text,
            )
            parsed_chunks.append(chunk)

        return self.index_chunks(parsed_chunks)

    def _rebuild_matrix(self) -> None:
        if not self.chunks:
            self.vocab = {}
            self.idf = np.array([])
            self.embeddings = np.array([])
            return

        tokenized_docs: List[List[str]] = []
        df_counter: Counter = Counter()

        for ch in self.chunks:
            composite_text = " ".join(
                [
                    ch.heading,
                    ch.heading,  # Boost heading weight
                    ch.category,
                    ch.policy_rule,
                    " ".join(ch.mandatory_requirements),
                    " ".join(ch.prohibited_terms),
                    ch.raw_excerpt,
                ]
            )
            tokens = self._tokenize(composite_text)
            tokenized_docs.append(tokens)
            for unique_t in set(tokens):
                df_counter[unique_t] += 1

        sorted_terms = sorted(df_counter.keys())
        self.vocab = {term: i for i, term in enumerate(sorted_terms)}
        n_docs = len(self.chunks)
        n_vocab = len(self.vocab)
        n_concepts = len(LEGAL_CONCEPT_CLUSTERS)

        self.idf = np.zeros(n_vocab, dtype=np.float64)
        for term, idx in self.vocab.items():
            self.idf[idx] = math.log((1.0 + n_docs) / (1.0 + df_counter[term])) + 1.0

        matrix = np.zeros((n_docs, n_vocab + n_concepts), dtype=np.float64)
        for doc_idx, tokens in enumerate(tokenized_docs):
            tf_counts = Counter(tokens)
            for term, count in tf_counts.items():
                t_idx = self.vocab[term]
                matrix[doc_idx, t_idx] = (1.0 + math.log(count)) * self.idf[t_idx]

            ch = self.chunks[doc_idx]
            concept_text = f"{ch.heading} {ch.category} {ch.policy_rule} {ch.raw_excerpt}"
            concept_vec = self._compute_concept_activations(concept_text)
            matrix[doc_idx, n_vocab:] = concept_vec

            norm = np.linalg.norm(matrix[doc_idx])
            if norm > 1e-9:
                matrix[doc_idx] /= norm

        self.embeddings = matrix

    def embed_query(self, query_text: str) -> np.ndarray:
        n_vocab = len(self.vocab)
        n_concepts = len(LEGAL_CONCEPT_CLUSTERS)
        vec = np.zeros(n_vocab + n_concepts, dtype=np.float64)
        tokens = self._tokenize(query_text)
        tf_counts = Counter(tokens)
        for term, count in tf_counts.items():
            if term in self.vocab:
                t_idx = self.vocab[term]
                vec[t_idx] = (1.0 + math.log(count)) * self.idf[t_idx]

        vec[n_vocab:] = self._compute_concept_activations(query_text)
        norm = np.linalg.norm(vec)
        if norm > 1e-9:
            vec /= norm
        return vec

    def search(
        self, query_text: str, top_k: int = 2, min_similarity: float = 0.18
    ) -> List[PlaybookReference]:
        """
        Retrieves the top_k most relevant PlaybookReference items above min_similarity
        using cosine similarity over the hybrid embedding space.
        """
        if not self.chunks or self.embeddings.size == 0:
            return []

        q_vec = self.embed_query(query_text)
        if np.linalg.norm(q_vec) < 1e-9:
            return []

        scores = np.dot(self.embeddings, q_vec)
        ranked_indices = np.argsort(scores)[::-1]

        results: List[PlaybookReference] = []
        for idx in ranked_indices[:top_k]:
            sim = float(scores[idx])
            if sim < min_similarity:
                continue
            ch = self.chunks[int(idx)]
            results.append(
                PlaybookReference(
                    chunk_id=ch.chunk_id,
                    document_id=ch.document_id,
                    document_title=ch.document_title,
                    section_ref=ch.section_ref,
                    heading=ch.heading,
                    category=ch.category,
                    governing_policy_rule=ch.policy_rule,
                    supporting_excerpt=ch.raw_excerpt,
                    similarity_score=round(sim, 4),
                    preferred_wording_template=ch.preferred_wording_template,
                    fallback_position=ch.fallback_position,
                )
            )
        return results
