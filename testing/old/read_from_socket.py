import socket

HOST = "192.168.0.223"
PORT = 2115

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))

    while True:
        data, addr = s.recvfrom(4096)
        # print(f"Recvd {len(data)} bytes from {addr}")
        print(f"{data}")