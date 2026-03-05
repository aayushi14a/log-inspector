from smolagents import Tool
import pandas as pd


class LogLoaderTool(Tool):
    name = "log_loader"
    description = (
        "Loads an Intuit service log CSV file and returns a profile of the log data "
        "including shape, columns, log level distribution, top error codes, "
        "services involved, and sample entries."
    )
    inputs = {
        "file_path": {
            "type": "string",
            "description": "Relative or absolute path to the log CSV file.",
        }
    }
    output_type = "string"

    def forward(self, file_path: str) -> str:
        try:
            df = pd.read_csv(file_path)
            total = len(df)

            # Log level distribution
            level_counts = df["level"].value_counts().to_string()

            # Top error codes (non-empty)
            error_codes = (
                df[df["error_code"].notna()]["error_code"]
                .value_counts()
                .head(10)
                .to_string()
            )

            # Services involved
            services = df["service"].value_counts().to_string()

            # Status code distribution
            status_codes = df["status_code"].dropna().astype(int).value_counts().to_string()

            # CRITICAL and ERROR entries
            critical_errors = df[df["level"].isin(["CRITICAL", "ERROR"])][
                ["timestamp", "level", "service", "message", "error_code"]
            ].to_string(index=False)

            # Slow requests (response_time > 5000ms)
            slow = df[df["response_time_ms"] > 5000]
            slow_str = (
                slow[["timestamp", "service", "message", "response_time_ms"]].to_string(index=False)
                if len(slow) > 0
                else "None"
            )

            summary = (
                f"=== LOG FILE PROFILE ===\n"
                f"File: {file_path}\n"
                f"Total entries: {total}\n"
                f"Columns: {list(df.columns)}\n\n"
                f"--- Log Level Distribution ---\n{level_counts}\n\n"
                f"--- Services ---\n{services}\n\n"
                f"--- HTTP Status Codes ---\n{status_codes}\n\n"
                f"--- Top Error Codes ---\n{error_codes}\n\n"
                f"--- CRITICAL & ERROR Entries ---\n{critical_errors}\n\n"
                f"--- Slow Requests (>5s) ---\n{slow_str}\n"
            )
            return summary
        except Exception as e:
            return f"Error loading log file: {e}"
