"""Sequential TCP echo server for loopback networking experiments."""

import argparse
import socket


def serve(host: str = "127.0.0.1", port: int = 8080) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen()
        actual_host, actual_port = server.getsockname()
        print(f"Listening on {actual_host}:{actual_port}", flush=True)

        while True:
            conn, addr = server.accept()
            print(f"Connected: {addr}", flush=True)
            with conn:
                while True:
                    data = conn.recv(4096)
                    if not data:  # EOF: the peer closed its sending direction
                        break
                    conn.sendall(data)
            print(f"Disconnected: {addr}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sequential TCP echo server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    try:
        serve(args.host, args.port)
    except KeyboardInterrupt:
        print("\nServer stopped")
