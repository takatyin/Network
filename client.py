"""Simple TCP echo client."""

import argparse
import socket


def echo(message: bytes, host: str = "127.0.0.1", port: int = 8080) -> bytes:
    with socket.create_connection((host, port), timeout=5) as conn:
        conn.settimeout(5)
        conn.sendall(message)
        conn.shutdown(socket.SHUT_WR)

        # TCP is a byte stream: a single recv may return fewer bytes.
        chunks = []
        while True:
            data = conn.recv(4096)
            if not data:
                break
            chunks.append(data)
        return b"".join(chunks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TCP echo client")
    parser.add_argument("message", nargs="?", default="Hello TCP")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    response = echo(args.message.encode(), args.host, args.port)
    print(response.decode(errors="replace"))
