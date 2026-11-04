# Network

Hands-on computer networking experiments based on concepts from *Computer Networks: A Systems Approach* (Peterson and Davie, v6.1).

## 01 — Threaded TCP Echo Server (Python)

A minimal TCP server implemented using Python's standard `socket` library, without a web framework.

### Run (Linux / WSL)

Terminal 1:

```bash
python3 server.py
```

Terminal 2:

```bash
python3 client.py "Hello TCP"
```

Expected client output:

```text
Hello TCP
```

The server binds to `127.0.0.1:8080` by default, so only programs on the same machine can connect. Use Ctrl+C to stop it.

### Test

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pytest tests/test_threading.py -q
python3 -m unittest discover -s tests -v
```

Tests start an actual server process on an ephemeral loopback port and check small messages, binary payloads, empty payloads, and sequential connections.

### How it works

```text
client.py                          server.py
  create_connection()                socket()
         |                           bind()
         |                           listen()
         +---- TCP connection -----> accept()
  sendall(bytes)  -----------------> recv(4096)
  recv(...)       <----------------- sendall(bytes)
  shutdown(write) -----------------> recv() == b''
  close()                           close(client connection)
```

The listening socket remains open while `accept()` returns a separate connected socket. TCP carries an **ordered byte stream**, not discrete application messages; one `recv()` does not necessarily correspond to one `sendall()`.

The client uses `shutdown(SHUT_WR)` to signal end-of-input while continuing to read echoed bytes until EOF. This is a **half-close**, not a separate network protocol.

### Known limitation

Each accepted connection is handled in its own daemon thread; the main thread returns to `accept()` without waiting for the current client's `recv()`. This is a learning example: there is no thread-count limit, client timeout, or graceful worker shutdown.

### Next iterations

- Add limits on concurrent connections and per-client timeouts
- Separate PR: event-driven I/O using `selectors`
- Comparative load tests: latency, throughput, and connection concurrency

### References

- Peterson & Davie, *Computer Networks: A Systems Approach*, §1.4.1 (Sockets) and §5.2 (TCP)
