import socket, os, time
import threading

SOCKET_PATH = "/tmp/infer.sock"
if os.path.exists(SOCKET_PATH):
    os.unlink(SOCKET_PATH)

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(SOCKET_PATH)
server.listen()
print("Daemon listening...")

def handle_request(conn):
    data = conn.recv(1024)
    print("Received:", data.decode().strip())
    time.sleep(2)              # fake work
    conn.sendall(b"OK " + data)
    conn.close()

while True:
    conn, _ = server.accept()
    thread = threading.Thread(target = handle_request, args = (conn,))
    thread.start()