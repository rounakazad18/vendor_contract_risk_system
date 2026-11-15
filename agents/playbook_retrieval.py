"""
Agent 2: Playbook Retrieval Agent
"""

from __future__ import annotations
import logging
from typing import List, Tuple
from schemas import ClauseRecord, PlaybookReference
from shared_memory import SharedClauseTable
from vector_store import PlaybookVectorStore
from framework_adapter import kernel_function

logger = logging.getLogger(__name__)


class PlaybookRetrievalAgent:
    AGENT_NAME = "PlaybookRetrievalAgent"

    def __init__(self, vector_store: PlaybookVectorStore, min_similarity: float = 0.20) -> None:
        self.vector_store = vector_store
        self.min_similarity = min_similarity

    @kernel_function(
        name="retrieve_governing_playbook_rule_tool",
        description="Runs RAG semantic search over the internal company playbook and returns the governing rule and citation.",
    )
    async def retrieve_for_clause(
        self, clause: ClauseRecord, shared_table: SharedClauseTable, top_k: int = 2
    ) -> Tuple[List[PlaybookReference], bool]:
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
