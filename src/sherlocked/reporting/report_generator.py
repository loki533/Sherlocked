
from pathlib import Path
from datetime import datetime
import json

from sherlocked.utils.paths import REPORTS_DIR


class ReportGenerator:
    """
    Generates investigation reports for Sherlocked cases.

    The generator currently produces a human-readable Markdown report
    and a JSON report containing the available case information.
    """

    @staticmethod
    def generate(case):
        """
        Generate a report for the supplied Case object.

        Args:
            case: Sherlocked Case instance.

        Returns:
            Path: Path to the generated Markdown report.
        """

        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        case_id = getattr(case, "case_id", "unknown_case")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        report_dir = REPORTS_DIR / str(case_id)
        report_dir.mkdir(parents=True, exist_ok=True)

        report_path = (
            report_dir /
            f"investigation_report_{timestamp}.md"
        )

        report_data = ReportGenerator._case_to_dict(case)

        report = ReportGenerator._build_markdown_report(
            report_data
        )

        report_path.write_text(
            report,
            encoding="utf-8"
        )

        # Also save a machine-readable JSON version.
        json_path = (
            report_dir /
            f"investigation_report_{timestamp}.json"
        )

        json_path.write_text(
            json.dumps(
                report_data,
                indent=4,
                default=str
            ),
            encoding="utf-8"
        )

        return report_path

    @staticmethod
    def _case_to_dict(case):
        """
        Convert a Case object into a dictionary without assuming
        every optional forensic attribute exists.
        """

        if hasattr(case, "to_dict"):
            try:
                data = case.to_dict()

                if isinstance(data, dict):
                    return data
            except Exception:
                pass

        return {
            "case_id": getattr(case, "case_id", None),
            "investigator": getattr(case, "investigator", None),
            "description": getattr(case, "description", None),
            "evidence_path": getattr(case, "evidence_path", None),
            "created_at": getattr(case, "created_at", None),
            "hashes": getattr(case, "hashes", {}),
            "metadata": getattr(case, "metadata", []),
            "timeline": getattr(case, "timeline", []),
            "recovered_files": getattr(case, "recovered_files", []),
            "mft_records": getattr(case, "mft_records", []),
        }

    @staticmethod
    def _build_markdown_report(data):
        """
        Build the human-readable investigation report.
        """

        case_id = data.get("case_id", "Unknown")
        investigator = data.get("investigator", "Unknown")
        description = data.get("description", "No description provided.")
        evidence_path = data.get("evidence_path", "Not specified")
        created_at = data.get("created_at", "Unknown")

        hashes = data.get("hashes", {})
        metadata = data.get("metadata", [])
        timeline = data.get("timeline", [])
        recovered_files = data.get("recovered_files", [])
        mft_records = data.get("mft_records", [])

        lines = []

        lines.append("# Sherlocked Digital Forensic Investigation Report")
        lines.append("")

        lines.append("## Case Information")
        lines.append("")
        lines.append(f"- **Case ID:** {case_id}")
        lines.append(f"- **Investigator:** {investigator}")
        lines.append(f"- **Created:** {created_at}")
        lines.append(f"- **Evidence:** `{evidence_path}`")
        lines.append("")

        lines.append("## Case Description")
        lines.append("")
        lines.append(str(description))
        lines.append("")

        lines.append("## Evidence Hashes")
        lines.append("")

        if hashes:
            lines.append("| File | Hash |")
            lines.append("|---|---|")

            for file_path, file_hash in hashes.items():
                lines.append(
                    f"| `{file_path}` | `{file_hash}` |"
                )
        else:
            lines.append("No evidence hashes recorded.")

        lines.append("")

        lines.append("## Metadata")
        lines.append("")

        if metadata:
            for item in metadata:
                if isinstance(item, dict):
                    lines.append("### Evidence Item")
                    lines.append("")

                    for key, value in item.items():
                        lines.append(
                            f"- **{key}:** {value}"
                        )

                    lines.append("")
                else:
                    lines.append(f"- {item}")
        else:
            lines.append("No metadata recorded.")

        lines.append("")

        lines.append("## Timeline")
        lines.append("")

        if timeline:
            lines.append("| Timestamp | Event |")
            lines.append("|---|---|")

            for event in timeline:
                if isinstance(event, dict):
                    timestamp = (
                        event.get("timestamp")
                        or event.get("time")
                        or event.get("date")
                        or "Unknown"
                    )

                    description = (
                        event.get("description")
                        or event.get("event")
                        or event.get("action")
                        or str(event)
                    )

                    lines.append(
                        f"| {timestamp} | {description} |"
                    )
                else:
                    lines.append(
                        f"| Unknown | {event} |"
                    )
        else:
            lines.append("No timeline events recorded.")

        lines.append("")

        lines.append("## NTFS MFT Records")
        lines.append("")

        if mft_records:
            lines.append("| Record | Name | Status | Type | Created | Modified |")
            lines.append("|---:|---|---|---|---|---|")
            for record in mft_records:
                names = record.get("file_names", [])
                name = names[0].get("filename", "") if names else ""
                status = "Allocated" if record.get("flags_decoded", {}).get("in_use") else "Deleted/Unused"
                kind = "Directory" if record.get("flags_decoded", {}).get("directory") else "File"
                created = names[0].get("created", "") if names else ""
                modified = names[0].get("modified", "") if names else ""
                lines.append(f"| {record.get('record_number')} | `{name}` | {status} | {kind} | {created} | {modified} |")
        else:
            lines.append("No MFT records recorded.")

        lines.append("")

        lines.append("## Recovered Files")
        lines.append("")

        if recovered_files:
            for file_path in recovered_files:
                lines.append(f"- `{file_path}`")
        else:
            lines.append("No recovered files recorded.")

        lines.append("")

        lines.append("## Investigation Summary")
        lines.append("")

        lines.append(
            "This report was generated automatically by "
            "Sherlocked Digital Forensic Investigation Toolkit."
        )

        lines.append("")

        lines.append(
            f"_Report generated on "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"
        )

        lines.append("")

        return "\n".join(lines)

