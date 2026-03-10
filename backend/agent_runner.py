import os
import sys
import asyncio
import threading
from pathlib import Path

# Add parent dir so we can import tools/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from smolagents import CodeAgent, InferenceClientModel
from tools.log_loader import LogLoaderTool
from tools.doc_reader import DocReaderTool
from tools.report_writer import ReportWriterTool

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")


async def run_agent_stream(logs_path: str, docs_path: str = None):
    """Run the smolagent and yield SSE events for each step."""
    # Absolute path for the report so it always lands in the project root output/
    report_path = Path(__file__).resolve().parent.parent / "output" / "incident_report.txt"

    hf_token = os.getenv("HF_TOKEN")
    model_id = os.getenv("HF_MODEL_ID", "Qwen/Qwen2.5-Coder-32B-Instruct")

    yield {"type": "status", "content": "Initializing Log Inspector agent..."}
    yield {"type": "step", "step": 0, "content": f"Connecting to model: {model_id}"}

    model = InferenceClientModel(model_id=model_id, token=hf_token)

    tools = [LogLoaderTool(), ReportWriterTool()]
    if docs_path:
        tools.append(DocReaderTool())

    agent = CodeAgent(
        tools=tools,
        model=model,
        additional_authorized_imports=[
            "pandas", "matplotlib", "seaborn", "json", "csv",
            "os", "collections", "re", "io",
        ],
        stream_outputs=False,
    )

    # Build task
    task = f"""
    You are an SRE engineer.You triage and analyse logs. Analyze the log file, identify issues quickly and accurately, and write an incident report.

    Step 1: Use the log_loader tool to load '{logs_path}'.
    Step 2: From the output, identify the log type, detect error messages, and any failures.
    Step 3: Extract the most relevant log entries that are related to failure.
    Step 4: Identify the likely root cause and any cascading failures.
    Step 5: Write an incident report covering:
       - Executive Summary
       - Possible Root Cause & Key Log Evidence
       - Timeline of errors
       - Affected Services
       - Cascading Failures (if any)
       - Immediate Actions
       - Long-term Fixes
    Step 6: Use the report_writer tool to save the report to '{report_path}'.
    """

    if docs_path:
        task += f"""
    Also: Read '{docs_path}' using the doc_reader tool and use it to improve your recommendations.
    """

    # Ensure output directory exists
    report_path.parent.mkdir(parents=True, exist_ok=True)

    yield {"type": "step", "step": 1, "content": "Agent task prepared. Starting analysis..."}

    # Run agent in a thread so we don't block the event loop
    result_holder = {"result": None, "error": None}

    def run_sync():
        try:
            result_holder["result"] = agent.run(task)
        except Exception as e:
            result_holder["error"] = str(e)

    thread = threading.Thread(target=run_sync)
    thread.start()

    step = 2
    while thread.is_alive():
        await asyncio.sleep(3)
        # Check agent's step log for progress
        if hasattr(agent, "logs") and agent.logs:
            num_steps = len(agent.logs)
            if num_steps >= step:
                for i in range(step - 1, num_steps):
                    log_entry = agent.logs[i]
                    # Extract step info
                    content = ""
                    if hasattr(log_entry, "model_output"):
                        content = str(log_entry.model_output)[:500] if log_entry.model_output else ""
                    elif hasattr(log_entry, "observations"):
                        content = str(log_entry.observations)[:500] if log_entry.observations else ""
                    
                    if not content and hasattr(log_entry, "__dict__"):
                        for key, val in log_entry.__dict__.items():
                            if val and key not in ("step_number",):
                                content = f"{key}: {str(val)[:300]}"
                                break

                    yield {
                        "type": "step",
                        "step": step,
                        "content": content or f"Processing step {step}...",
                    }
                    step += 1
        else:
            yield {"type": "thinking", "content": f"Agent is working (step ~{step})..."}

    thread.join()

    if result_holder["error"]:
        yield {"type": "error", "content": result_holder["error"]}
    else:
        # Read the generated report
        report_path = Path(__file__).resolve().parent.parent / "output" / "incident_report.txt"
        report_content = ""
        if report_path.exists():
            report_content = report_path.read_text(encoding="utf-8")

        yield {
            "type": "complete",
            "content": report_content,
            "summary": str(result_holder["result"])[:2000] if result_holder["result"] else "",
        }
