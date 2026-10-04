import socket
import os

SOCKET_PATH = "/tmp/infer.sock"

# Remove old socket if it exists
if os.path.exists(SOCKET_PATH):
    os.unlink(SOCKET_PATH)

# Create Unix socket
server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Give it a local address
server.bind(SOCKET_PATH)

# Start listening
server.listen()

print("Daemon listening...")
print(f"Socket: {SOCKET_PATH}")

# Wait for a client
conn, _ = server.accept()

print("Client connected!")

# Receive request
data = conn.recv(1024)

print("Received:", data.decode())

# Send response
conn.sendall(b"OK " + data)

# Close client connection
conn.close()

# Close listening socket
server.close()