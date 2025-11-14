import socket
import msgpack
import math
import matplotlib.pyplot as plt

# ---------------- UDP setup ----------------
HOST = "192.168.0.223"  # Your PC's IP
PORT = 2115              # LiDAR port

# ---------------- MsgPack helpers ----------------
def ext_hook(code, data):
    """Handle MsgPack extension types."""
    return (code, data)

def decode_obj(o):
    """Recursively decode MsgPack object:
       - Convert bytes to strings when safe
       - Convert unhashable dict keys to strings
    """
    if isinstance(o, dict):
        new_dict = {}
        for k, v in o.items():
            try:
                key = decode_obj(k)
                hash(key)
            except TypeError:
                key = str(decode_obj(k))
            new_dict[key] = decode_obj(v)
        return new_dict
    elif isinstance(o, list):
        return [decode_obj(i) for i in o]
    elif isinstance(o, bytes):
        try:
            return o.decode("utf-8")
        except UnicodeDecodeError:
            return o
    else:
        return o

def extract_points(obj):
    """Recursively search decoded MsgPack object for distance+angle arrays and return (x, y) points."""
    points = []

    if isinstance(obj, dict):
        keys = obj.keys()
        # Attempt to find Distance + ChannelTheta pairs
        distance = obj.get('Distance') or obj.get(b'Distance')
        angles = obj.get('ChannelTheta') or obj.get(b'ChannelTheta')
        if distance and angles and len(distance) == len(angles):
            for r, a in zip(distance, angles):
                # Convert mm to meters if necessary
                r_m = r / 1000 if r > 100 else r
                # Assume angles are in radians
                points.append((r_m * math.cos(a), r_m * math.sin(a)))
        else:
            # Recursively search values
            for v in obj.values():
                points.extend(extract_points(v))
    elif isinstance(obj, list):
        for item in obj:
            points.extend(extract_points(item))

    return points

# ---------------- Matplotlib setup ----------------
plt.ion()
fig, ax = plt.subplots()
scatter = ax.scatter([], [])
ax.set_xlim(-10, 10)  # Adjust to your LiDAR range in meters
ax.set_ylim(-10, 10)
ax.set_aspect('equal')

# ---------------- Socket & Unpacker ----------------
unpacker = msgpack.Unpacker(raw=True, strict_map_key=False, ext_hook=ext_hook)

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.bind((HOST, PORT))
    print(f"Listening for SICK MSGPACK on UDP {HOST}:{PORT} ...")

    while True:
        try:
            data, addr = sock.recvfrom(65535)
            unpacker.feed(data)

            for msg in unpacker:
                decoded = decode_obj(msg)

                # Extract (x, y) points
                points = extract_points(decoded)
                if points:
                    xs, ys = zip(*points)
                    scatter.set_offsets(list(zip(xs, ys)))
                    ax.relim()
                    ax.autoscale_view()
                    plt.draw()
                    plt.pause(0.001)

        except KeyboardInterrupt:
            print("Exiting...")
            break
        except Exception as e:
            print("Error:", e)
