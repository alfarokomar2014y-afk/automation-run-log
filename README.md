# automation-run-log

[![Python tests](https://github.com/alfarokomar2014y-afk/automation-run-log/actions/workflows/tests.yml/badge.svg)](https://github.com/alfarokomar2014y-afk/automation-run-log/actions/workflows/tests.yml)

A small **local-first Python command-line utility** for recording automation run outcomes as JSON Lines (`.jsonl`) and generating readable Markdown summaries. It does not connect to GitHub, collect telemetry, or make network requests.

**Version:** v0.3.0 candidate (pull request, not yet released). Not intended as a secure audit ledger, secret store, or central production logging service.

## Requirements

- Python 3.10 or later
- No third-party runtime dependencies

Run commands from the repository root. No installation is necessary for module mode.

## Quick start

Preview a fictional example without writing files:

```bash
python -m automation_run_log report --file examples/sample_runs.jsonl
```

Record your own test run in a local log:

```bash
python -m automation_run_log add --file my_runs.jsonl --task demo-job --status success --duration-ms 250
python -m automation_run_log report --file my_runs.jsonl --output report.md
```

The `add` command appends one JSON object per line; `report` reads the log and prints a summary, or writes a **new** Markdown file with `--output`. To avoid accidental data loss, the tool will not overwrite existing reports or its input log.

Optional `--timestamp` must use ISO 8601 and include a timezone, e.g. `2026-11-01T10:00:00Z`. The default is current UTC. `--duration-ms` must be a finite non-negative number. Status is one of `success`, `failed`, or `skipped`.

## New in v0.3.0

Export CSV for Excel (new file only):

```bash
python -m automation_run_log report --file examples/sample_runs.jsonl --format csv --output results.csv
```

Filter by inclusive UTC dates:

```bash
python -m automation_run_log report --file examples/sample_runs.jsonl --from 2026-11-01 --to 2026-11-01
```

Markdown output now includes a **Failed runs** section. CSV exports include timestamp, task, status and duration_ms columns. Saved CSV files use UTF-8 BOM for Excel and prefix formula-like fields with an apostrophe to reduce spreadsheet formula injection risks. Date filters compare the timestamp in UTC, including offset conversion. Always review untrusted data before opening it in a spreadsheet.

## Example JSONL record

```json
{"timestamp":"2026-11-01T08:00:00Z","task":"fictional-task","status":"success","duration_ms":1200}
```

## Tests

```bash
python -m unittest discover -s tests -v
```

## Data handling and limitations

- All bundled example records are synthetic. **Your own logs stay on your computer** unless you choose to share them.
- No automatic redaction or encryption: **never pass passwords, tokens, personal information, or sensitive task names** to the CLI. Review any report before sharing it.
- A malformed record stops reporting and identifies its line number; the original log is left unchanged.
- Files are local and not tamper-evident or transaction-safe for multiple concurrent writers.
- Markup in task names is escaped in Markdown tables, but this does not make logging untrusted information safe for other contexts.

## Community and release notes

- [Contributing guidelines](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
- [v0.2.0 release notes](RELEASE_NOTES_v0.2.0.md)
- [v0.3.0 draft notes](RELEASE_NOTES_v0.3.0_DRAFT.md)

## Licence

MIT licence. Copyright (c) 2026 MrNoOne.
