import socket
import struct

HOST = "192.168.0.223"
PORT = 2115

def parse_picoscan150_compact(data: bytes):
    """Parse a picoScan150 Compact-format UDP packet."""
    if len(data) <= 32:
        return None

    if data[:4] != b"\x02\x02\x02\x02":
        print("Bad header:", data[:4])
        return None

    payload_len = len(data) - 32
    num_points = payload_len // 2  # 2 bytes per distance
    distances = struct.unpack_from(f"<{num_points}H", data, 32)
    return distances

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        print(f"Listening for picoScan150 Compact data on {HOST}:{PORT}")

        while True:
            data, addr = s.recvfrom(65535)
            distances = parse_picoscan150_compact(data)
            if distances:
                print(f"Got {len(distances)} distance values. First 10:", distances[:10])
            else:
                print(f"Unparsed packet ({len(data)} bytes)")

if __name__ == "__main__":
    main()
