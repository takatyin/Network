"""Thread-per-connection TCP echo server for loopback experiments."""

import argparse
import socket
import threading


def handle_client(conn: socket.socket) -> None:
    with conn:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            conn.sendall(data)


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
            threading.Thread(target=handle_client, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Threaded TCP echo server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    try:
        serve(args.host, args.port)
    except KeyboardInterrupt:
        print("\nServer stopped")
