import os
import argparse
try:
    import pip_system_certs  # noqa: corporate proxy support (Windows only)
except ImportError:
    pass
from dotenv import load_dotenv
from smolagents import CodeAgent, InferenceClientModel
from tools.log_loader import LogLoaderTool
from tools.doc_reader import DocReaderTool
from tools.report_writer import ReportWriterTool

load_dotenv()

# ── Everything below only runs when executed directly (not on import) ────────
if __name__ == "__main__":

    # ── CLI arguments ─────────────────────────────────────────────────────────
    parser = argparse.ArgumentParser(description="Log Inspector - A log triaging AI Agent")
    parser.add_argument(
        "--docs",
        type=str,
        default=None,
        help="Optional path to a reference doc (best practices, runbook, .txt/.md/.py/.docx) "
             "that the agent will use to give better fix recommendations.",
    )
    parser.add_argument(
        "--logs",
        type=str,
        default="data/intuit_logs.csv",
        help="Path to the log CSV file to analyze (default: data/intuit_logs.csv).",
    )
    args = parser.parse_args()

    # ── Model setup ──────────────────────────────────────────────────────────
    # Model: Qwen/Qwen2.5-Coder-32B-Instruct (open-source, 32B params)
    # Hosted on: HuggingFace Inference API (remote, no local GPU needed)
    # Auth: HF_TOKEN from .env file → sent via API to HF servers
    hf_token = os.getenv("HF_TOKEN")
    model_id = os.getenv("HF_MODEL_ID", "Qwen/Qwen2.5-Coder-32B-Instruct")

    model = InferenceClientModel(model_id=model_id, token=hf_token)

    # ── Agent setup ───────────────────────────────────────────────────────────
    agent = CodeAgent(
        tools=[LogLoaderTool(), DocReaderTool(), ReportWriterTool()],
        model=model,
        additional_authorized_imports=["pandas", "matplotlib", "seaborn", "json", "csv", "os", "collections", "re"],
        stream_outputs=True,
    )

    # ── Build the task ────────────────────────────────────────────────────────
    # Base task — always runs
    task = f"""
    You are an SRE engineer. Analyze the log file and write an incident report.

    Step 1: Use the log_loader tool to load '{args.logs}'.
    Step 2: From the output, identify the root cause (the first error) and any cascading failures.
    Step 3: Write an incident report covering:
       - Executive Summary
       - Root Cause
       - Timeline of errors
       - Affected Services
       - Cascading Failures
       - Immediate Actions
       - Long-term Fixes
    Step 4: Use the report_writer tool to save the report to 'output/incident_report.txt'.
    """

    # If --docs is provided, inject the reference document into the task
    if args.docs:
        task += f"""
    Also: Read '{args.docs}' using the doc_reader tool and use it to improve your recommendations.
    """
        print(f"[INFO] Reference document loaded: {args.docs}")
    else:
        print("[INFO] No reference doc provided. Use --docs <path> to improve recommendations.")

    agent.run(task)
