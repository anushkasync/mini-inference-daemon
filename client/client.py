import socket
import time

SOCKET_PATH = "/tmp/infer.sock"

for i in range(1, 6):
    start = time.perf_counter()

    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    client.connect(SOCKET_PATH)

    client.sendall(f"req{i}".encode())

    response = client.recv(1024)

    end = time.perf_counter()
    latency = end - start

    print(f"{response.decode()} in {latency:.2f}s")

    client.close()

