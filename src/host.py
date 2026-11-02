import socket

HOST = "127.0.0.1"
MY_PORT = 5001

R1_IP = "127.0.0.1"
R1_PORT = 5002

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind((HOST, MY_PORT))

print(f"H1 is running on {HOST}:{MY_PORT}")

message = "Hello from H1"

sock.sendto(message.encode(), (R1_IP, R1_PORT))

print(f"H1 sent: {message}")