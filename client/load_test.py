
import socket
import time
import statistics
import concurrent.futures

SOCKET_PATH = "/tmp/inference_daemon.sock"

REQUEST_COUNTS = [5, 10, 25, 50, 100]
CLIENT_WORKERS = 100
TIMEOUT_SECONDS = 60


def send_request(request_id):
    start = time.perf_counter()

    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(TIMEOUT_SECONDS)
            client.connect(SOCKET_PATH)
            client.sendall(f"request-{request_id}\n".encode())

            response = b""
            while not response.endswith(b"\n"):
                chunk = client.recv(4096)
                if not chunk:
                    break
                response += chunk

        elapsed = time.perf_counter() - start

        if not response:
            return {
                "id": request_id,
                "latency": elapsed,
                "success": False,
                "error": "Empty response",
            }

        if response.startswith(b"ERROR: 503"):
            return {
                "id": request_id,
                "latency": elapsed,
                "success": False,
                "error": "Rejected: server overloaded (503)",
            }

        if not response.startswith(b"OK "):
            return {
                "id": request_id,
                "latency": elapsed,
                "success": False,
                "error": f"Unexpected response: {response!r}",
            }

        return {
            "id": request_id,
            "latency": elapsed,
            "success": True,
            "error": None,
        }

    except Exception as exc:
        return {
            "id": request_id,
            "latency": time.perf_counter() - start,
            "success": False,
            "error": str(exc),
        }


def percentile(values, p):
    values = sorted(values)
    index = max(0, (len(values) * p + 99) // 100 - 1)
    return values[min(index, len(values) - 1)]


def run_test(request_count):
    print(f"\n--- {request_count} requests ---")

    start = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=min(CLIENT_WORKERS, request_count)
    ) as executor:
        futures = [
            executor.submit(send_request, i)
            for i in range(request_count)
        ]
        results = [future.result() for future in futures]

    total_time = time.perf_counter() - start
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    latencies = [r["latency"] for r in successful]

    print(f"Completed: {len(successful)}/{request_count}")
    print(f"Failed:    {len(failed)}")
    print(f"Total time: {total_time:.3f} s")
    print(f"Throughput: {len(successful) / total_time:.2f} requests/s")

    if latencies:
        print(f"Latency P50: {percentile(latencies, 50):.3f} s")
        print(f"Latency P95: {percentile(latencies, 95):.3f} s")
        print(f"Latency P99: {percentile(latencies, 99):.3f} s")
        print(f"Mean latency: {statistics.mean(latencies):.3f} s")

    if failed:
        print("Sample errors:")
        for result in failed[:5]:
            print(f"  Request {result['id']}: {result['error']}")


if __name__ == "__main__":
    for count in REQUEST_COUNTS:
        run_test(count)
