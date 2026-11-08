"""Regression tests for date filters, CSV export, and failure summaries."""
import contextlib
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path
from automation_run_log.cli import export_csv, filter_dates, main, parse_date, summarize


def run_record(ts, task='job', status='success', duration=None):
    record = {'timestamp': ts, 'task': task, 'status': status}
    if duration is not None:
        record['duration_ms'] = duration
    return record


class Version03Tests(unittest.TestCase):
    def setUp(self):
        self.records = [
            run_record('2026-11-01T23:30:00-02:00', 'offset-job', 'failed', 900),
            run_record('2026-11-02T03:00:00Z', 'routine', 'success', 100),
            run_record('2026-11-03T00:00:00Z', 'later', 'skipped'),
        ]

    def test_inclusive_utc_date_bounds(self):
        selected = filter_dates(self.records, '2026-11-02', '2026-11-02')
        self.assertEqual([r['task'] for r in selected], ['offset-job', 'routine'])

    def test_only_from(self):
        self.assertEqual(len(filter_dates(self.records, '2026-11-03')), 1)

    def test_only_to(self):
        self.assertEqual(len(filter_dates(self.records, to_date='2026-11-02')), 2)

    def test_unfiltered(self):
        self.assertEqual(len(filter_dates(self.records)), 3)

    def test_empty_range(self):
        self.assertEqual(filter_dates(self.records, '2027-01-01', '2027-01-02'), [])

    def test_invalid_date_format(self):
        for value in ('11/02/2026', '2026-1-02', '20261102', ''):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_date(value)

    def test_invalid_day(self):
        with self.assertRaises(ValueError):
            parse_date('2026-02-30')

    def test_reversed_dates(self):
        with self.assertRaisesRegex(ValueError, '--from'):
            filter_dates(self.records, '2026-11-03', '2026-11-02')

    def test_csv_valid_columns(self):
        rows = list(csv.DictReader(io.StringIO(export_csv(self.records))))
        self.assertEqual(list(rows[0]), ['timestamp', 'task', 'status', 'duration_ms'])
        self.assertEqual(rows[0]['duration_ms'], '900')
        self.assertEqual(rows[-1]['duration_ms'], '')

    def test_csv_quotes_commas_and_newlines(self):
        value = 'complex,"two"\nlines'
        rows = list(csv.DictReader(io.StringIO(export_csv([run_record('2026-11-02T00:00:00Z', value)]))))
        self.assertEqual(rows[0]['task'], value)

    def test_csv_formula_safety(self):
        for dangerous in ('=2+2', '+cmd', '-SUM(1,2)', '@abc', '\t=1+2', '   =1+1'):
            with self.subTest(dangerous=dangerous):
                parsed = next(csv.DictReader(io.StringIO(export_csv([run_record('2026-11-02T00:00:00Z', dangerous)]))))
                self.assertEqual(parsed['task'], "'" + dangerous)

    def test_safe_csv_task_unchanged(self):
        row = next(csv.DictReader(io.StringIO(export_csv([run_record('2026-11-02T00:00:00Z', 'normal-job')]))))
        self.assertEqual(row['task'], 'normal-job')

    def test_failed_section_shows_only_failures(self):
        summary = summarize(self.records)
        section = summary.split('## Failed runs', 1)[1]
        self.assertIn('offset-job', section)
        self.assertNotIn('routine', section)
        self.assertNotIn('later', section)

    def test_no_failed_runs_message(self):
        self.assertIn('No failed runs', summarize(self.records[1:]))

    def test_cli_csv_output_utf8_bom(self):
        with tempfile.TemporaryDirectory() as d:
            src, dest = Path(d) / 'input.jsonl', Path(d) / 'output.csv'
            src.write_text('\n'.join(json.dumps(r) for r in self.records), encoding='utf-8')
            self.assertEqual(main(['report', '--file', str(src), '--format', 'csv', '--output', str(dest), '--from', '2026-11-02', '--to', '2026-11-02']), 0)
            self.assertTrue(dest.read_bytes().startswith(b'\xef\xbb\xbf'))
            with dest.open(encoding='utf-8-sig', newline='') as stream:
                self.assertEqual(len(list(csv.DictReader(stream))), 2)

    def test_cli_invalid_range_does_not_write(self):
        with tempfile.TemporaryDirectory() as d:
            src, dest = Path(d) / 'input.jsonl', Path(d) / 'output.csv'
            src.write_text(json.dumps(self.records[0]) + '\n', encoding='utf-8')
            with self.assertRaises(SystemExit) as raised, contextlib.redirect_stderr(io.StringIO()):
                main(['report', '--file', str(src), '--format', 'csv', '--output', str(dest), '--from', '2026-11-03', '--to', '2026-11-02'])
            self.assertEqual(raised.exception.code, 2)
            self.assertFalse(dest.exists())

    def test_cli_csv_reject_overwrite_input(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / 'input.jsonl'
            src.write_text(json.dumps(self.records[0]) + '\n', encoding='utf-8')
            before = src.read_bytes()
            with self.assertRaises(SystemExit) as raised, contextlib.redirect_stderr(io.StringIO()):
                main(['report', '--file', str(src), '--format', 'csv', '--output', str(src)])
            self.assertEqual(raised.exception.code, 2)
            self.assertEqual(src.read_bytes(), before)

    def test_cli_csv_reject_existing_report(self):
        with tempfile.TemporaryDirectory() as d:
            src, dest = Path(d) / 'input.jsonl', Path(d) / 'output.csv'
            src.write_text(json.dumps(self.records[0]) + '\n', encoding='utf-8')
            dest.write_text('existing', encoding='utf-8')
            with self.assertRaises(SystemExit) as raised, contextlib.redirect_stderr(io.StringIO()):
                main(['report', '--file', str(src), '--format', 'csv', '--output', str(dest)])
            self.assertEqual(raised.exception.code, 2)
            self.assertEqual(dest.read_text(encoding='utf-8'), 'existing')


if __name__ == '__main__':
    unittest.main()
