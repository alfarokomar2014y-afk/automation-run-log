# Release notes — v0.2.0

**automation-run-log** is a lightweight, local-first Python CLI for recording the outcome of automation tasks and summarising them as readable Markdown.

## Highlights

- Append timestamped run records to a local JSONL file.
- Report counts of successful, failed, and skipped runs.
- Display average recorded duration when available.
- Includes an illustrative synthetic dataset and 19 unit tests.
- Tested locally on Windows with Python 3.14.3.

## Quick start

```bash
python -m automation_run_log report --file examples/sample_runs.jsonl
python -m unittest discover -s tests -v
```

## Compatibility

Python 3.10+; uses only the standard library at runtime. The GitHub Actions workflow checks Linux and Windows across multiple Python versions.

## Important limitations

No automatic redaction or encryption; never include personal data, private automation logs, secrets, or credentials. This tool is not tamper-evident and should not be used as a regulated audit trail.

## License

MIT — Copyright (c) 2026 MrNoOne.

*These notes are prepared for the GitHub Release page. The GitHub Release is only official once the tag and release entry have been created.*
