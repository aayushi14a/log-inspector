from smolagents import Tool
import os


class ReportWriterTool(Tool):
    name = "report_writer"
    description = (
        "Writes a text report to a file. "
        "Creates the output directory automatically if it does not exist."
    )
    inputs = {
        "file_path": {
            "type": "string",
            "description": "Path where the report will be saved (e.g. 'output/report.txt').",
        },
        "content": {
            "type": "string",
            "description": "The full text content to write into the report file.",
        },
    }
    output_type = "string"

    def forward(self, file_path: str, content: str) -> str:
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Report successfully written to '{file_path}'."
        except Exception as e:
            return f"Error writing report: {e}"
