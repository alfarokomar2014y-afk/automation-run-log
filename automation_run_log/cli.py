"""Local JSON Lines automation run logging and Markdown reporting."""

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re

STATUSES = ("success", "failed", "skipped")


def validate(record):
    """Validate one JSON-compatible run record; return it unchanged."""
    if not isinstance(record, dict):
        raise ValueError("record must be a JSON object")
    for field in ("task", "status", "timestamp"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            raise ValueError(f"{field} must be a non-empty string")
    if record["status"] not in STATUSES:
        raise ValueError("status must be success, failed or skipped")
    try:
        timestamp = datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("timestamp must be a valid ISO 8601 datetime") from exc
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("timestamp must include a timezone (Z or an offset)")
    if "duration_ms" in record:
        duration = record["duration_ms"]
        if type(duration) not in (int, float) or not math.isfinite(duration) or duration < 0:
            raise ValueError("duration_ms must be a finite non-negative number")
    return record


def load(path):
    """Read and validate newline-separated JSON records with line diagnostics."""
    records = []
    with Path(path).open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                # parse_constant rejects non-standard JSON NaN and Infinity literals.
                value = json.loads(line, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f"non-JSON constant {x}")))
                records.append(validate(value))
            except (ValueError, TypeError) as exc:
                raise ValueError(f"Invalid record at line {number}: {exc}") from exc
    return records


def markdown_cell(value):
    """Render untrusted text as a single literal Markdown table cell."""
    text = str(value).replace("\\", "\\\\").replace("|", "\\|")
    text = re.sub(r"[\r\n\t\x00-\x1f\x7f]", " ", text)
    for token in ("\x60", "*", "_", "[", "]", "<", ">", "!", "~"):
        text = text.replace(token, "\\" + token)
    return text


def summarize(records):
    """Build an inspectable Markdown report from validated run records."""
    checked = [validate(record) for record in records]
    counts = {status: sum(row["status"] == status for row in checked) for status in STATUSES}
    durations = [row["duration_ms"] for row in checked if "duration_ms" in row]
    lines = [
        "# Automation Run Report", "",
        f"Total runs: {len(checked)}",
        f"Successful: {counts['success']}",
        f"Failed: {counts['failed']}",
        f"Skipped: {counts['skipped']}",
    ]
    if durations:
        lines.append(f"Average recorded duration: {sum(durations) / len(durations):.0f} ms")
    lines += ["", "## Runs", "", "| Timestamp | Task | Status |", "| --- | --- | --- |"]
    for row in checked:
        lines.append(f"| {markdown_cell(row['timestamp'])} | {markdown_cell(row['task'])} | {markdown_cell(row['status'])} |")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Record local automation runs and produce Markdown reports")
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add", help="Append a run to a JSONL file")
    add.add_argument("--file", required=True)
    add.add_argument("--task", required=True)
    add.add_argument("--status", required=True, choices=STATUSES)
    add.add_argument("--duration-ms", type=float)
    add.add_argument("--timestamp", help="ISO 8601 with timezone; default: current UTC")
    report = commands.add_parser("report", help="Summarize a JSONL file as Markdown")
    report.add_argument("--file", required=True)
    report.add_argument("--output", help="Markdown output file; default: stdout")
    args = parser.parse_args(argv)
    try:
        if args.command == "add":
            record = {
                "timestamp": args.timestamp or datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "task": args.task,
                "status": args.status,
            }
            if args.duration_ms is not None:
                record["duration_ms"] = args.duration_ms
            validate(record)  # Validate before creating or altering any file.
            destination = Path(args.file)
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
            print("Run recorded.")
        else:
            source = Path(args.file)
            output = Path(args.output) if args.output else None
            if output is not None and source.resolve() == output.resolve():
                raise ValueError("output must differ from the source log file")
            rendered = summarize(load(source))
            if output is not None:
                # Do not silently create folders or overwrite a report.
                with output.open("x", encoding="utf-8") as handle:
                    handle.write(rendered)
                print(f"Report written to {output}")
            else:
                print(rendered, end="")
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
