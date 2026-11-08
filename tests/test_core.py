"""Automated tests for core CLI behavior, including failure paths."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from automation_run_log.cli import load, main, markdown_cell, summarize, validate

GOOD = {"task": "task-a", "status": "success", "timestamp": "2026-11-01T00:00:00Z"}


class RunLogTests(unittest.TestCase):
    def test_valid_record(self):
        self.assertEqual(validate(GOOD)["status"], "success")

    def test_invalid_status(self):
        with self.assertRaises(ValueError):
            validate({**GOOD, "status": "unknown"})

    def test_negative_duration(self):
        with self.assertRaises(ValueError):
            validate({**GOOD, "duration_ms": -1})

    def test_non_finite_duration(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate({**GOOD, "duration_ms": value})

    def test_boolean_duration(self):
        with self.assertRaises(ValueError):
            validate({**GOOD, "duration_ms": True})

    def test_bad_timestamp(self):
        with self.assertRaises(ValueError):
            validate({**GOOD, "timestamp": "not-a-date"})

    def test_naive_timestamp(self):
        with self.assertRaises(ValueError):
            validate({**GOOD, "timestamp": "2026-11-01T00:00:00"})

    def test_timezone_offset(self):
        validate({**GOOD, "timestamp": "2026-11-01T01:00:00+01:00"})

    def test_empty_log(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "empty.jsonl"
            source.write_text("\n", encoding="utf-8")
            self.assertIn("Total runs: 0", summarize(load(source)))

    def test_load_and_report(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "runs.jsonl"
            source.write_text(json.dumps({**GOOD, "status": "failed"}) + "\n", encoding="utf-8")
            self.assertIn("Failed: 1", summarize(load(source)))

    def test_line_number_on_bad_record(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "bad.jsonl"
            source.write_text(json.dumps(GOOD) + "\n{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "line 2"):
                load(source)

    def test_reject_nonstandard_json(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "bad.jsonl"
            source.write_text(json.dumps({**GOOD, "duration_ms": float("nan")}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "line 1"):
                load(source)

    def test_escape_markdown_table(self):
        name = "job|**bad**\nnext [link](x) <tag>"
        report = summarize([{**GOOD, "task": name}])
        self.assertIn("job\\|\\*\\*bad\\*\\* next", report)
        self.assertIn("\\<tag\\>", report)
        self.assertNotIn("\nnext", report)

    def test_escape_backslashes(self):
        self.assertEqual(markdown_cell("a\\|b"), "a\\\\\\|b")

    def test_add_then_report(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "runs.jsonl"
            self.assertEqual(main(["add", "--file", str(source), "--task", "test", "--status", "success"]), 0)
            self.assertEqual(len(load(source)), 1)
            destination = Path(directory) / "report.md"
            self.assertEqual(main(["report", "--file", str(source), "--output", str(destination)]), 0)
            self.assertIn("Successful: 1", destination.read_text(encoding="utf-8"))

    def test_reject_overwrite_source(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "runs.jsonl"
            data = json.dumps(GOOD) + "\n"
            source.write_text(data, encoding="utf-8")
            with self.assertRaises(SystemExit) as caught, contextlib.redirect_stderr(io.StringIO()):
                main(["report", "--file", str(source), "--output", str(source)])
            self.assertEqual(caught.exception.code, 2)
            self.assertEqual(source.read_text(encoding="utf-8"), data)

    def test_reject_overwrite_existing_report(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "runs.jsonl"
            source.write_text(json.dumps(GOOD) + "\n", encoding="utf-8")
            destination = Path(directory) / "report.md"
            destination.write_text("original", encoding="utf-8")
            with self.assertRaises(SystemExit) as caught, contextlib.redirect_stderr(io.StringIO()):
                main(["report", "--file", str(source), "--output", str(destination)])
            self.assertEqual(caught.exception.code, 2)
            self.assertEqual(destination.read_text(encoding="utf-8"), "original")

    def test_reject_invalid_add_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "runs.jsonl"
            with self.assertRaises(SystemExit) as caught, contextlib.redirect_stderr(io.StringIO()):
                main(["add", "--file", str(source), "--task", "job", "--status", "success", "--duration-ms", "nan"])
            self.assertEqual(caught.exception.code, 2)
            self.assertFalse(source.exists())

    def test_failed_command_on_missing_source(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(SystemExit) as caught, contextlib.redirect_stderr(io.StringIO()):
                main(["report", "--file", str(Path(directory) / "missing.jsonl")])
            self.assertEqual(caught.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
