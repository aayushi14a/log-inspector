from smolagents import Tool
import pandas as pd


class CSVLoaderTool(Tool):
    name = "csv_loader"
    description = (
        "Loads a CSV file from a given path and returns a summary of its contents "
        "including shape, column names, dtypes, and the first few rows as a string."
    )
    inputs = {
        "file_path": {
            "type": "string",
            "description": "Relative or absolute path to the CSV file.",
        }
    }
    output_type = "string"

    def forward(self, file_path: str) -> str:
        try:
            df = pd.read_csv(file_path)
            summary = (
                f"File: {file_path}\n"
                f"Shape: {df.shape[0]} rows x {df.shape[1]} columns\n"
                f"Columns: {list(df.columns)}\n"
                f"Dtypes:\n{df.dtypes.to_string()}\n\n"
                f"First 5 rows:\n{df.head().to_string(index=False)}\n\n"
                f"Basic stats:\n{df.describe(include='all').to_string()}"
            )
            return summary
        except Exception as e:
            return f"Error loading CSV: {e}"
