import socket
import os
import time
from concurrent.futures import ThreadPoolExecutor

SOCKET_PATH = "/tmp/inference_daemon.sock"

if os.path.exists(SOCKET_PATH):
    os.unlink(SOCKET_PATH)

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(SOCKET_PATH)
server.listen(128)
print("🆔 Server PID:", os.getpid())
print("🚨 Tier 2 ThreadPool Daemon listening...")

def handle_request(conn):
    try:
        data = conn.recv(1024)
        
        # --- THE SAME BRUTAL MATH LOOP ---
        acc = 0
        for _ in range(5_000_000):
            acc += 1234 * 5678
            
        conn.sendall(b"OK " + data + b"\n") 
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def run_server():
    # Pre-allocate exactly 4 threads (Caps hardware usage)
    with ThreadPoolExecutor(max_workers=4) as executor:
        while True:
            conn, _ = server.accept()
            # Submit to the internal thread-safe task queue
            executor.submit(handle_request, conn)

if __name__ == "__main__":
    try:
        run_server()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        if os.path.exists(SOCKET_PATH):
            os.unlink(SOCKET_PATH)

