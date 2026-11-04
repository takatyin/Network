"""Check that one idle client does not block another client's echo."""

import re
import socket
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
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
        assert match, f"Server did not start: {line!r}"
        yield int(match.group(1))
    finally:
        process.terminate()
        try:
            process.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()


def test_idle_client_does_not_block_another_client(server_port):
    with socket.create_connection(("127.0.0.1", server_port), timeout=2) as idle:
        # Keep the first connection open, without sending any data.
        with socket.create_connection(("127.0.0.1", server_port), timeout=2) as active:
            active.settimeout(2)
            active.sendall(b"Hello TCP")
            active.shutdown(socket.SHUT_WR)
            chunks = []
            while data := active.recv(4096):
                chunks.append(data)
            assert b"".join(chunks) == b"Hello TCP"
