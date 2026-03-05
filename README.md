# Log Inspector - A log triaging AI Agent

An autonomous SRE/log analysis agent powered by [smolagents](https://github.com/huggingface/smolagents) and the HuggingFace Inference API.

## What it does

- Loads raw production service logs and profiles them
- Identifies CRITICAL/ERROR events, cascading failures, and slow requests
- Performs root cause analysis autonomously using pandas code
- Generates a structured incident report

## LLM Details

| | |
|---|---|
| **Model** | `Qwen/Qwen2.5-Coder-32B-Instruct` (open-source, 32B params) |
| **Hosted on** | HuggingFace Inference API (remote servers, no local GPU) |
| **Auth** | `HF_TOKEN` in `.env` — sent via API to HF infrastructure |
| **Cost** | Free tier available; pay-per-token for heavy usage |

## Project Structure

```
.
├── main.py              # Entry point (supports --docs and --logs args)
├── tools/
│   ├── log_loader.py    # Tool: loads logs, profiles errors/services
│   ├── doc_reader.py    # Tool: reads local docs (.txt/.md/.docx/.py)
│   ├── csv_loader.py    # Tool: generic CSV loader
│   └── report_writer.py # Tool: writes analysis reports to disk
├── docs/
│   └── sre_best_practices.md  # Sample best practices runbook
├── data/
│   └── intuit_logs.csv  # Raw production log dataset
├── output/              # Incident reports saved here
├── requirements.txt
└── .env                 # Your HF token (copy from .env.example)
```

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure your API token**
   ```bash
   cp .env.example .env
   # Edit .env and add your HuggingFace token
   ```
   Get your token at: https://huggingface.co/settings/tokens

3. **Run the agent**
   ```bash
   python main.py
   ```

## Usage

**Basic run (no docs):**
```bash
python main.py
```

**With a reference document (best practices, runbook, etc.):**
```bash
python main.py --docs docs/sre_best_practices.md
```

**With a custom log file:**
```bash
python main.py --logs data/other_logs.csv
```

**Both together:**
```bash
python main.py --logs data/intuit_logs.csv --docs docs/sre_best_practices.md
```

Supported doc formats: `.txt`, `.md`, `.py`, `.json`, `.csv`, `.log`, `.docx`

## What the agent does (step by step)

1. Loads `data/intuit_logs.csv` via the `log_loader` tool
2. Reads the full CSV into pandas for deeper analysis
3. Groups CRITICAL/ERROR events by service and error code
4. Detects cascading failures and slow requests (>5s)
5. Flags security concerns (brute force, DDoS, webhook attacks)
6. Builds a timeline of incidents
7. **(If --docs provided)** Reads the reference document and uses it for recommendations
8. Writes a full incident report to `output/incident_report.txt`

## Log dataset

The dataset in `data/intuit_logs.csv` is a realistic raw production log containing:
- **85+ entries** across 12+ Intuit microservices
- Log levels: INFO, WARN, ERROR, CRITICAL
- Real error patterns: payment timeouts, OOM crashes, DB failovers, SSL failures, DDoS detection
- Java stack traces, retry logic, cascading failures
- Services: api-gateway, auth-service, tax-calc-engine, payment-service, doc-service, etc.
