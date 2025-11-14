import socket
import matplotlib.pyplot as plt
import numpy as np

# LiDAR IP and port (same as before)
IP = "192.168.0.223"
PORT = 2115

def get_scan():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((IP, PORT))
        # Request scan data
        s.sendall(b"sRN LMDscandata\n")
        data = b""
        while True:
            part = s.recv(4096)
            if not part:
                break
            data += part
            if b"\n" in part:  # stop at end of response
                break
    return data.decode()

def parse_scan(data):
    lines = data.split("\n")
    # Find the line starting with "DIST1" which contains distances
    for line in lines:
        if line.startswith("DIST1"):
            dist_strs = line.split()[1:]  # skip "DIST1"
            distances = np.array([int(d) for d in dist_strs])
            return distances
    return np.array([])

def plot_scan(distances, angle_resolution=0.1):
    num_points = len(distances)
    angles = np.deg2rad(np.arange(0, num_points * angle_resolution, angle_resolution))
    x = distances * np.cos(angles)
    y = distances * np.sin(angles)
    
    plt.figure(figsize=(6,6))
    plt.scatter(x, y, s=1)
    plt.xlabel("X [mm]")
    plt.ylabel("Y [mm]")
    plt.title("LiDAR Scan")
    plt.axis("equal")
    plt.show()

if __name__ == "__main__":
    scan_data = get_scan()
    distances = parse_scan(scan_data)
    plot_scan(distances)
