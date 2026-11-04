"""Integration tests using a real local TCP connection."""

import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

from client import echo


ROOT = Path(__file__).resolve().parents[1]


class EchoServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.process = subprocess.Popen(
            [sys.executable, "-u", str(ROOT / "server.py"), "--port", "0"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        line = cls.process.stdout.readline()
        match = re.fullmatch(r"Listening on 127\.0\.0\.1:(\d+)\n", line)
        if not match:
            cls.process.terminate()
            raise RuntimeError(f"Server failed to start: {line!r}")
        cls.port = int(match.group(1))

    @classmethod
    def tearDownClass(cls):
        cls.process.terminate()
        try:
            cls.process.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            cls.process.kill()
            cls.process.communicate()

    def test_small_message(self):
        self.assertEqual(echo(b"Hello TCP", port=self.port), b"Hello TCP")

    def test_empty_message(self):
        self.assertEqual(echo(b"", port=self.port), b"")

    def test_binary_and_large_message(self):
        payload = bytes(range(256)) * 64
        self.assertEqual(echo(payload, port=self.port), payload)

    def test_sequential_connections(self):
        for message in (b"first", b"second", b"third"):
            self.assertEqual(echo(message, port=self.port), message)


if __name__ == "__main__":
    unittest.main()
