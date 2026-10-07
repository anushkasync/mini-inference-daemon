import socket, os

SOCKET_PATH = "/tmp/infer.sock"

client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

client.connect(SOCKET_PATH)

client.sendall(b"Hello")

response = client.recv(1024)

print(response.decode())

client.close()