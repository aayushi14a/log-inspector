from smolagents import Tool
import pandas as pd


class LogLoaderTool(Tool):
    name = "log_loader"
    description = (
        "Loads an Intuit service log CSV file and returns structured insights "
        "including log distribution, service error counts, incident clusters, "
        "security alerts, and slow requests."
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

            # Ensure timestamp is datetime
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

            # Log level distribution
            level_counts = df["level"].value_counts().to_string()

            # Services involved
            services = df["service"].value_counts().to_string()

            # HTTP status code distribution
            status_codes = (
                df["status_code"].dropna().astype(int).value_counts().to_string()
                if "status_code" in df.columns
                else "No status_code column"
            )

            # Top error codes
            error_codes = (
                df[df["error_code"].notna()]["error_code"]
                .value_counts()
                .head(10)
                .to_string()
            )

            # Error count by service
            service_errors = (
                df[df["level"].isin(["ERROR", "CRITICAL"])]
                .groupby("service")
                .size()
                .sort_values(ascending=False)
                .to_string()
            )

            # CRITICAL and ERROR entries
            critical_errors = df[df["level"].isin(["CRITICAL", "ERROR"])][
                ["timestamp", "level", "service", "message", "error_code"]
            ].head(20).to_string(index=False)

            # Incident clusters (spikes of errors per second)
            incident_clusters = (
                df[df["level"].isin(["ERROR", "CRITICAL"])]
                .groupby(df["timestamp"].dt.floor("S"))
                .size()
                .sort_values(ascending=False)
                .head(5)
                .to_string()
            )

            # Security alerts
            security_events = df[df["error_code"].astype(str).str.contains("SEC", na=False)]
            security_summary = (
                security_events[["timestamp", "service", "error_code"]]
                .to_string(index=False)
                if len(security_events) > 0
                else "None"
            )

            # Slow requests
            slow = df[df["response_time_ms"] > 5000]
            slow_str = (
                slow[["timestamp", "service", "message", "response_time_ms"]]
                .head(10)
                .to_string(index=False)
                if len(slow) > 0
                else "None"
            )

            # Possible cascade (first few error events in order)
            cascade = (
                df[df["level"].isin(["ERROR", "CRITICAL"])]
                .sort_values("timestamp")[
                    ["timestamp", "service", "error_code"]
                ]
                .head(20)
                .to_string(index=False)
            )

            summary = (
                f"=== LOG FILE PROFILE ===\n"
                f"File: {file_path}\n"
                f"Total entries: {total}\n"
                f"Columns: {list(df.columns)}\n\n"

                f"--- Log Level Distribution ---\n{level_counts}\n\n"

                f"--- Services Involved ---\n{services}\n\n"

                f"--- HTTP Status Codes ---\n{status_codes}\n\n"

                f"--- Top Error Codes ---\n{error_codes}\n\n"

                f"--- Error Count by Service ---\n{service_errors}\n\n"

                f"--- Incident Time Clusters (Error Spikes) ---\n{incident_clusters}\n\n"

                f"--- Possible Failure Cascade ---\n{cascade}\n\n"

                f"--- Security Alerts ---\n{security_summary}\n\n"

                f"--- Slow Requests (>5s) ---\n{slow_str}\n\n"

                f"--- Sample CRITICAL & ERROR Entries ---\n{critical_errors}\n"
            )

            return summary

        except Exception as e:
            return f"Error loading log file: {e}"