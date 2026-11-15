"""
Main Entry Point & End-to-End Pipeline Runner (`main.py`)
Group 2: Gursirat Singh (12326116) & Rounak Azad (12326217)
"""

from __future__ import annotations
import asyncio
import json
import logging
import os
import sys

from agents import ReviewManagerAgent
from data.sample_data import populate_default_vector_store, generate_sample_contract_files
from report_generator import generate_report_html

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("VendorContractSystem")


async def run_pipeline(output_html_path: str, output_json_path: str) -> None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sample_dir = os.path.join(base_dir, "data", "generated_samples")
    sample_files = generate_sample_contract_files(sample_dir)

    vector_store = populate_default_vector_store()
    manager = ReviewManagerAgent(vector_store=vector_store, max_concurrency=6)

    def _log_progress(stage: str, pct: int) -> None:
        logger.info("[%3d%%] %s", pct, stage)

    report = await manager.analyze_contract_file(
        file_path=sample_files["docx"],
        contract_prefix="APEX",
        progress_callback=_log_progress,
    )

    html_content = generate_report_html(report)
    os.makedirs(os.path.dirname(os.path.abspath(output_html_path)), exist_ok=True)
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(report.to_dict(), f, indent=2)

    logger.info("Saved HTML report to %s", output_html_path)
    logger.info("Saved JSON report to %s", output_json_path)


if __name__ == "__main__":
    out_html = (
        sys.argv[1]
        if len(sys.argv) > 1
        else os.path.join(os.path.dirname(__file__), "report.html")
    )
    out_json = (
        sys.argv[2]
        if len(sys.argv) > 2
        else os.path.join(os.path.dirname(__file__), "report.json")
    )
    asyncio.run(run_pipeline(out_html, out_json))
