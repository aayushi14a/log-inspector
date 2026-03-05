from smolagents import Tool
import os


class DocReaderTool(Tool):
    name = "doc_reader"
    description = (
        "Reads a local document file and returns its text content. "
        "Supports .txt, .md, .py, .json, .csv, .log, and .docx files. "
        "Use this to read best practices, runbooks, or reference documents."
    )
    inputs = {
        "file_path": {
            "type": "string",
            "description": "Path to the document file to read.",
        }
    }
    output_type = "string"

    def forward(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' not found."

        ext = os.path.splitext(file_path)[1].lower()

        try:
            # Handle .docx files
            if ext == ".docx":
                return self._read_docx(file_path)

            # Handle all text-based files
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if not content.strip():
                return f"File '{file_path}' is empty."

            return f"=== Contents of {file_path} ===\n\n{content}"

        except UnicodeDecodeError:
            return f"Error: Cannot read '{file_path}' — binary file or unsupported encoding."
        except Exception as e:
            return f"Error reading '{file_path}': {e}"

    def _read_docx(self, file_path: str) -> str:
        try:
            from docx import Document
        except ImportError:
            return (
                "Error: python-docx package not installed. "
                "Run: pip install python-docx"
            )

        doc = Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        content = "\n\n".join(paragraphs)

        if not content.strip():
            return f"File '{file_path}' is empty."

        return f"=== Contents of {file_path} ===\n\n{content}"
