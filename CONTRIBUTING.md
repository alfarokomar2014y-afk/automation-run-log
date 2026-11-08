# Contributing to automation-run-log

Thanks for helping improve this small, local-first project.

## Before submitting a change

- Open an issue describing a bug or proposed improvement when possible.
- Keep changes focused and avoid adding external runtime dependencies without discussion.
- Never submit real automation logs, usernames, email addresses, API keys, credentials, or internal project data.
- Use invented, synthetic data in tests, examples and screenshots.

## Development

Requires Python 3.10+.

```bash
python -m unittest discover -s tests -v
python -m automation_run_log report --file examples/sample_runs.jsonl
```

Please add tests for changed behavior and keep the README and changelog accurate.

## Pull requests

Describe what changed, why it matters, and how you tested it. Public pull requests are subject to review; passing CI does not automatically approve or merge a change.

## Reporting security concerns

Please don't post credentials, private logs, or exploit details in public issues. If you discover a potential security vulnerability, contact the maintainer through an appropriate private GitHub channel rather than attaching sensitive material to an issue.
