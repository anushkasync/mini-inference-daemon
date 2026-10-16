import socket
import os
import time
import threading

print(f"🆔 Server PID: {os.getpid()}")

# Make sure this matches your client script path exactly!
SOCKET_PATH = "/tmp/inference_daemon.sock"

if os.path.exists(SOCKET_PATH):
    os.unlink(SOCKET_PATH)

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(SOCKET_PATH)
server.listen(128) # Increased backlog to absorb the 100-request burst
print("🚨 Sabotaged Daemon listening for pure CPU math...")

def handle_request(conn):
    try:
        data = conn.recv(1024)
        
        # --- THE HARDWARE SABOTAGE: Pure CPU-bound math loop ---
        # This keeps the M2 core running hot and refuses to release the GIL
        acc = 0
        for _ in range(5_000_000):
            acc += 1234 * 5678
            
        # Send a tiny response back to signal completion
        conn.sendall(b"OK " + data + b"\n") 
    except Exception as e:
        print(f"Error handling request: {e}")
    finally:
        conn.close()

try:
    while True:
        conn, _ = server.accept()
        thread = threading.Thread(target=handle_request, args=(conn,))
        thread.start()
except KeyboardInterrupt:
    print("\nShutting down server...")
finally:
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)
