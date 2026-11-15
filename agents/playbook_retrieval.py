"""
Agent 2: Playbook Retrieval Agent
Responsibilities:
- Implement Retrieval-Augmented Generation (RAG) over the company's internal contract playbook.
- Retrieve relevant playbook sections for each contract clause.
- Identify the governing company policy or contractual rule.
- Return the relevant playbook reference, supporting context, and source information.
- Provide accurate references rather than generating unsupported policies.
- Explicitly flag clauses when no matching playbook reference exists.
"""

from __future__ import annotations
import logging
from typing import List, Tuple
from schemas import ClauseRecord, PlaybookReference
from shared_memory import SharedClauseTable
from vector_store import PlaybookVectorStore

logger = logging.getLogger(__name__)


class PlaybookRetrievalAgent:
    """
    Agent 2: Queries the PlaybookVectorStore for each extracted contract clause,
    identifies governing company policies with exact citations, and updates the
    SharedClauseTable without fabricating policies.
    """

    AGENT_NAME = "PlaybookRetrievalAgent"

    def __init__(self, vector_store: PlaybookVectorStore, min_similarity: float = 0.20) -> None:
        self.vector_store = vector_store
        self.min_similarity = min_similarity

    async def retrieve_for_clause(
        self, clause: ClauseRecord, shared_table: SharedClauseTable, top_k: int = 2
    ) -> Tuple[List[PlaybookReference], bool]:
        """
        Retrieves applicable playbook sections for a single ClauseRecord and updates
        SharedClauseTable. Explicitly marks missing_playbook_reference=True if no
        playbook rule exceeds the minimum similarity threshold.
        """
        query = f"{clause.clause_heading} {clause.clause_heading} {clause.original_text}"
        references = self.vector_store.search(
            query_text=query, top_k=top_k, min_similarity=self.min_similarity
        )

        if not references:
            logger.info(
                "No matching playbook policy found for Clause %s ('%s'). Marking missing_playbook_reference=True.",
                clause.clause_id,
                clause.clause_heading,
            )
            await shared_table.update_playbook_retrieval(
                clause_id=clause.clause_id,
                references=[],
                policy_rules=[
                    "NO_MATCHING_PLAYBOOK_POLICY: No governing internal playbook rule found for this clause topic; manual legal review required if non-standard obligations exist."
                ],
                missing_reference=True,
            )
            return [], True

        policy_rules = [
            f"[{ref.section_ref} — {ref.heading}] {ref.governing_policy_rule}"
            for ref in references
        ]

        await shared_table.update_playbook_retrieval(
            clause_id=clause.clause_id,
            references=references,
            policy_rules=policy_rules,
            missing_reference=False,
        )
        return references, False
