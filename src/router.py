import socket

HOST = "127.0.0.1"
PORT = 5002

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind((HOST, PORT))

print(f"R1 is listening on {HOST}:{PORT}")

while True:
    data, address = sock.recvfrom(4096)

    message = data.decode()

    print(f"Received message: {message}")
    print(f"Sender UDP address: {address}")