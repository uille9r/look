import csv
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("summarize.py")
SAMPLES = Path(__file__).with_name("samples")


class SummarizeTests(unittest.TestCase):
    def run_cli(self, folder, output):
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(folder), str(output)],
            capture_output=True, text=True, encoding="utf-8",
        )

    def read_rows(self, output):
        with output.open(encoding="utf-8-sig", newline="") as file:
            return list(csv.reader(file))

    def test_samples_have_four_cues_in_filename_order(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "report.csv"
            result = self.run_cli(SAMPLES, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(self.read_rows(output), [["file", "cues"], ["片头.srt", "1"], ["访谈.srt", "3"]])
            self.assertTrue(output.read_bytes().startswith(b"\xef\xbb\xbf"))

    def test_uppercase_srt_suffix_is_counted(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary) / "mixed"
            folder.mkdir()
            (folder / "片尾.SRT").write_text(
                "1\n00:00:00,000 --> 00:00:02,000\n结束\n", encoding="utf-8"
            )
            (folder / "说明.txt").write_text("不是字幕\n", encoding="utf-8")
            output = Path(temporary) / "report.csv"
            result = self.run_cli(folder, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(self.read_rows(output), [["file", "cues"], ["片尾.SRT", "1"]])

    def test_empty_directory_still_has_header(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary) / "empty"
            folder.mkdir()
            output = Path(temporary) / "report.csv"
            result = self.run_cli(folder, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(self.read_rows(output), [["file", "cues"]])

    def test_missing_directory_has_chinese_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "report.csv"
            result = self.run_cli(Path(temporary) / "missing", output)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("输入目录不存在或不是目录", result.stderr)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
