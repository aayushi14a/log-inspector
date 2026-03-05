# Copilot Instructions

This is an **Intuit Log Analysis Agent** project using smolagents + HuggingFace Inference API.

## Stack
- Python 3.10+
- [smolagents](https://github.com/huggingface/smolagents) for the agent framework
- pandas / matplotlib / seaborn for data analysis
- HuggingFace Inference API (`InferenceClientModel`) with `Qwen/Qwen2.5-Coder-32B-Instruct`

## Key files
- `main.py` — agent entry point, log analysis task definition
- `tools/log_loader.py` — custom tool to load/profile production logs
- `tools/csv_loader.py` — generic CSV loader tool
- `tools/report_writer.py` — custom tool to write incident reports to disk
- `data/intuit_logs.csv` — raw production log dataset
- `output/` — generated incident reports

## Conventions
- All custom tools live in `tools/` and inherit from `smolagents.Tool`
- Tools must define `name`, `description`, `inputs`, `output_type`, and `forward()`
- Use `additional_authorized_imports` in the agent for any extra packages
- Never hardcode API tokens — always use `.env` via `python-dotenv`
- Output files always go to the `output/` directory
