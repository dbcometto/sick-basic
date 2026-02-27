import socket

HOST = "192.168.0.111"
PORT = 2115

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))
    print(f"Listening on {HOST}:{PORT}")

    while True:
        data, addr = s.recvfrom(65565)
        print(f"From {addr}, {len(data)} bytes:")
        print(" ".join(f"{b:02X}" for b in data))
        break  # stop after first packet
