import socket
import subprocess
import unittest


class EchoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server = subprocess.Popen(
            ["./tcp_echo", "0"], stdout=subprocess.PIPE, text=True
        )
        cls.addClassCleanup(server.stdout.close)
        cls.addClassCleanup(server.wait, timeout=3)
        cls.addClassCleanup(server.terminate)
        cls.port = int(server.stdout.readline())

    def connect(self):
        client = socket.create_connection(("127.0.0.1", self.port), timeout=2)
        self.addCleanup(client.close)
        return client

    def test_line_split_across_reads(self):
        client = self.connect()
        # The line exceeds the server's 1024-byte recv buffer.
        first = b"x" * 1500
        client.sendall(first)
        client.settimeout(0.1)
        with self.assertRaises(socket.timeout):
            client.recv(1)
        client.settimeout(2)
        client.sendall(b"end\n")
        with client.makefile("rb") as response:
            self.assertEqual(response.readline(), first + b"end\n")

    def test_multiple_lines_in_one_write(self):
        client = self.connect()
        client.sendall(b"hello\nworld\n")
        client.shutdown(socket.SHUT_WR)
        with client.makefile("rb") as response:
            self.assertEqual(response.read(), b"hello\nworld\n")

    def test_partial_line_at_eof(self):
        client = self.connect()
        client.sendall(b"incomplete")
        client.shutdown(socket.SHUT_WR)
        self.assertEqual(client.recv(1), b"")

    def test_line_length_limit(self):
        client = self.connect()
        line = b"x" * 4096 + b"\n"
        with client.makefile("rb") as response:
            client.sendall(line)
            self.assertEqual(response.readline(), line)
            client.sendall(b"x" * 4097)
            self.assertEqual(response.read(1), b"")


if __name__ == "__main__":
    unittest.main()
