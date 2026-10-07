import socket
import time
import threading

SOCKET_PATH = "/tmp/infer.sock"
results = []

def send_request(i):
    start = time.perf_counter()
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(SOCKET_PATH)
    client.sendall(f"req{i}".encode())
    response = client.recv(1024)
    latency = time.perf_counter() - start
    client.close()
    results.append((latency, response.decode().strip()))

t0 = time.perf_counter()

threads = []
for i in range(1, 6):
    t = threading.Thread(target=send_request, args=(i,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

total = time.perf_counter() - t0

for latency, reply in sorted(results):
    print(f"{reply} in {latency:.2f}s")
print(f"total: {total:.2f}s")