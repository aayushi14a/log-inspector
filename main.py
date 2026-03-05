import os
import argparse
import pip_system_certs  # Use Windows system certificate store (corporate proxy support)
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
    You are an SRE engineer at Intuit. Analyze the production service logs.

    1. Load the log file at '{args.logs}' using the log_loader tool.
    2. Read the full CSV into a pandas DataFrame for deeper analysis.
    3. Perform a root cause analysis:
       a. What are the CRITICAL and ERROR events? Group them by service and error_code.
       b. Are there cascading failures? (e.g., one service failure causing others)
       c. Which services have the highest error rates?
       d. Identify any slow requests (response_time_ms > 5000) and their root cause.
       e. Are there any security concerns in the logs?
       f. What is the timeline of incidents — which happened first, what followed?
    4. Produce an incident report with:
       - Executive Summary
       - Timeline of events
       - Top 5 most critical issues with root cause
       - Services affected
       - Recommended immediate actions
       - Long-term fixes
    5. Write the full incident report to 'output/incident_report.txt' using the report_writer tool.
    """

    # If --docs is provided, inject the reference document into the task
    if args.docs:
        task += f"""
    IMPORTANT — Reference Document:
    A best practices / runbook document has been provided at: '{args.docs}'
    6. Use the doc_reader tool to read '{args.docs}' BEFORE writing your recommendations.
    7. Base your "Recommended immediate actions" and "Long-term fixes" on the practices
       described in that document. Quote specific sections where relevant.
    8. If the document contains fix procedures for specific error codes found in the logs,
       include those exact steps in the report.
    """
        print(f"[INFO] Reference document loaded: {args.docs}")
    else:
        print("[INFO] No reference doc provided. Use --docs <path> to improve recommendations.")

    agent.run(task)
