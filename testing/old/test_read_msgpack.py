import socket
import msgpack

HOST = "192.168.0.223"
PORT = 2115

unpacker = msgpack.Unpacker(raw=True, strict_map_key=False)

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))
    print(f"Listening on {HOST}:{PORT}...")

    while True:
        data, addr = s.recvfrom(65535)
        print(f"Received {len(data)} bytes from {addr}")

        unpacker.feed(data[4:])

        unpacked = msgpack.unpackb(data[4:],strict_map_key=False)

        for msg in unpacked:
            print(f"Msg: {msg}")
