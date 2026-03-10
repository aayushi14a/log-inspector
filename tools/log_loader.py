from smolagents import Tool
import pandas as pd


class LogLoaderTool(Tool):
    name = "log_loader"
    description = (
        "Loads a log CSV file and returns a summary including column info, "
        "log level distribution, error entries, and slow requests if applicable."
    )

    inputs = {
        "file_path": {
            "type": "string",
            "description": "Path to the log CSV file.",
        }
    }

    output_type = "string"

    def forward(self, file_path: str) -> str:
        try:
            df = pd.read_csv(file_path)
            total = len(df)
            cols = list(df.columns)

            parts = [
                f"Total log entries: {total}",
                f"Columns: {cols}",
            ]

            # Log level distribution (look for common level column names)
            level_col = None
            for candidate in ["level", "severity", "log_level", "loglevel"]:
                if candidate in cols:
                    level_col = candidate
                    break

            if level_col:
                parts.append(f"\nLog Level Counts:\n{df[level_col].value_counts().to_string()}")

                # Error entries
                error_levels = ["ERROR", "CRITICAL", "FATAL", "error", "critical", "fatal"]
                errors = df[df[level_col].isin(error_levels)]
                if not errors.empty:
                    error_lines = []
                    for _, row in errors.iterrows():
                        error_lines.append(", ".join(str(row[c]) for c in cols))
                    parts.append(f"\nAll ERROR/CRITICAL entries ({len(errors)} total):")
                    parts.append("\n".join(error_lines))
                else:
                    parts.append("\nNo ERROR/CRITICAL entries found.")

            # Slow requests (look for response time column)
            time_col = None
            for candidate in ["response_time_ms", "response_time", "duration_ms", "latency_ms", "duration"]:
                if candidate in cols:
                    time_col = candidate
                    break

            if time_col:
                try:
                    slow = df[pd.to_numeric(df[time_col], errors="coerce") > 5000]
                    if not slow.empty:
                        slow_lines = []
                        for _, row in slow.iterrows():
                            slow_lines.append(", ".join(str(row[c]) for c in cols))
                        parts.append(f"\nSlow Requests (>{time_col} > 5000):")
                        parts.append("\n".join(slow_lines))
                    else:
                        parts.append("\nNo slow requests found.")
                except Exception:
                    pass

            # First 5 rows as sample
            sample_lines = []
            for _, row in df.head(5).iterrows():
                sample_lines.append(", ".join(str(row[c]) for c in cols))
            parts.append(f"\nSample entries (first 5):")
            parts.append("\n".join(sample_lines))

            return "\n".join(parts)

        except Exception as e:
            return f"Error loading log file: {e}"