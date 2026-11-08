# Changelog

All notable changes to this project are documented here.

## [0.3.0] - Unreleased

- CSV export suitable for Excel, with basic spreadsheet formula guards.
- Inclusive UTC date filters using --from and --to.
- Dedicated Markdown failed-runs section.
- 18 additional unit tests (37 total).

## [0.2.0] - 2026-11-08

Initial public release candidate.

### Added
- Local JSON Lines (JSONL) run recording via `add`.
- Markdown summaries via `report` with totals, status counts and average recorded duration.
- Synthetic sample log and CLI usage documentation.
- 19 unit tests, including malformed records and accidental overwrite protection.
- Windows local validation with Python 3.14.3.

### Safety and behavior
- Validates statuses, ISO 8601 timezone-aware timestamps, and finite nonnegative durations.
- Escapes Markdown-sensitive text in report tables.
- Refuses to overwrite an existing Markdown report or the input log.
- No network calls or telemetry, and no third-party runtime dependencies.

### Known limitations
- No encryption, automatic redaction, tamper-evident records, multi-writer coordination, or log rotation.
- Not a central production logging service.
