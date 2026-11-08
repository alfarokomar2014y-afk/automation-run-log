# Draft release notes — v0.3.0 (not published)

automation-run-log v0.3.0 adds CSV export for spreadsheet analysis, inclusive UTC calendar date filtering, and dedicated Markdown reporting for failed runs.

## Highlights

- `report --format csv` outputs an Excel-friendly CSV, using UTF-8 BOM when written to a file.
- `--from YYYY-MM-DD` and `--to YYYY-MM-DD` select records on inclusive UTC dates.
- Markdown reports include a separate **Failed runs** section.
- A basic CSV formula guard reduces spreadsheet injection risks.
- Tests expanded from 19 to 37.

## Examples

```bash
python -m automation_run_log report --file examples/sample_runs.jsonl --format csv --output results.csv
python -m automation_run_log report --file examples/sample_runs.jsonl --from 2026-11-01 --to 2026-11-01
```

## Verification

- Local development suite: 37/37 passed.
- Windows acceptance: 37/37 passed on Python 3.14.3. CSV, date filtering and failure reporting were also demonstrated manually.
- GitHub Actions checks: pending until this pull request completes.

## Safety and limitations

All bundled records are synthetic. This tool does not encrypt or automatically redact logs, and cannot serve as a secure audit trail. Do not share personal information, secrets, or private automation records. CSV formula hardening reduces risk but does not replace careful review before importing untrusted data.
