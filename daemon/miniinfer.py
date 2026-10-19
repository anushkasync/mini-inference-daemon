import socket
import os
import time
import signal
import sys
from concurrent.futures import ThreadPoolExecutor

SOCKET_PATH = "/tmp/inference_daemon.sock"
MAX_QUEUE_SIZE = 20  # If more than 20 requests are waiting, trigger backpressure
MAX_WORKERS = 4

server_socket = None
executor = None
backpressure_drops = 0

def handle_request(conn):
    try:
        data = conn.recv(1024)
        if not data:
            return
        
        # --- THE SAME SYSTEM MATH LOOP ---
        acc = 0
        for _ in range(5_000_000):
            acc += 1234 * 5678
            
        conn.sendall(b"OK " + data + b"\n") 
    except Exception as e:
        print(f"Worker Error: {e}")
    finally:
        conn.close()

def graceful_shutdown(signum, frame):
    """Triggered cleanly by the OS kernel when you hit Ctrl+C"""
    print("\n🛑 Shutdown signal caught. Initiating graceful exit...")
    
    if server_socket:
        server_socket.close()
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)
        
    if executor:
        print("⏳ Waiting for active worker threads to finish current math...")
        executor.shutdown(wait=True)
        
    print(f"📉 Total requests dropped by backpressure: {backpressure_drops}")
    print("👋 Daemon cleanly terminated. System memory released.")
    sys.exit(0)

def run_server():
    global server_socket, executor, backpressure_drops
    
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)

    # Register OS kernel signal triggers for Ctrl+C
    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)

    server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server_socket.bind(SOCKET_PATH)
    server_socket.listen(128)
    
    print("🆔 Server PID:", os.getpid())
    print(f"🚨 Hardened Tier-2 Daemon Ready (Max Queue Ceiling: {MAX_QUEUE_SIZE})")

    executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
    
    try:
        while True:
            try:
                conn, _ = server_socket.accept()
                
                # --- BACKPRESSURE CALCULATOR ---
                # Check how many tasks are currently sitting in the queue
                current_queue_depth = executor._work_queue.qsize()
                
                if current_queue_depth >= MAX_QUEUE_SIZE:
                    # Queue is full! Reject connection immediately to protect RAM
                    conn.sendall(b"ERROR: 503 Service Unavailable (Overloaded Queue)\n")
                    conn.close()
                    backpressure_drops += 1
                    continue
                
                # If space is safe, submit the task
                executor.submit(handle_request, conn)
            except OSError:
                break
    finally:
        if os.path.exists(SOCKET_PATH):
            os.unlink(SOCKET_PATH)

if __name__ == "__main__":
    run_server()
