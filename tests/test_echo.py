"""TCP echo integration tests against a real local server."""

import re
import subprocess
import sys
from pathlib import Path

import pytest

from client import echo


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def server_port():
    process = subprocess.Popen(
        [sys.executable, "-u", str(ROOT / "server.py"), "--port", "0"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        line = process.stdout.readline()
        match = re.fullmatch(r"Listening on 127\.0\.0\.1:(\d+)\n", line)
        if not match:
            pytest.fail(f"Server failed to start: {line!r}")
        yield int(match.group(1))
    finally:
        process.terminate()
        try:
            process.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()


@pytest.mark.parametrize("payload", [
    b"Hello TCP",
    b"",
    bytes(range(256)) * 64,
])
def test_echo(server_port, payload):
    assert echo(payload, port=server_port) == payload


def test_sequential_connections(server_port):
    for message in (b"first", b"second", b"third"):
        assert echo(message, port=server_port) == message
