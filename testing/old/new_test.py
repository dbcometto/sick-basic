import socket
import struct
import zlib
import msgpack
import numpy as np

UDP_IP = "192.168.0.223"
UDP_PORT = 2115
BUFFER_SIZE = 65536

# MSGPACK keyword mapping
KEYWORDS = {
    0x10: "classname",
    0x11: "data",
    0x12: "numOfElems",
    0x13: "elemSz",
    0x14: "endian",
    0x15: "elemTypes",
    0x50: "ChannelTheta",
    0x51: "ChannelPhi",
    0x52: "DistValues",
    0x53: "RssiValues",
    0x54: "PropertyValues",
    0x70: "Scan",
    0x71: "TimeStampStart",
    0x72: "TimeStampStop",
    0x73: "ThetaStart",
    0x74: "ThetaStop",
    0x75: "ScanNumber",
    0x76: "ModuleId",
    0x77: "BeamCount",
    0x78: "EchoCount",
    0x90: "ScanSegment",
    0x91: "SegmentCounter",
    0x92: "FrameNumber",
    0x93: "Availability",
    0x94: "SenderId",
    0x96: "SegmentData",
    0xA0: "LayerId",
    0xB0: "TelegramCounter"
}

# Class codes
SCANSEGMENT_CLASSCODE = 0x90
SCAN_CLASSCODE = 0x70

def parse_array(array_dict):
    """Parse a measurement array into a NumPy array, handling buffer size mismatch."""
    if not isinstance(array_dict, dict):
        return np.array([], dtype=np.float32)

    data_bytes = array_dict.get(b'data', array_dict.get("data", b""))
    elem_type_code = array_dict.get(0x15, [0x31])[0]
    elem_sz = array_dict.get(0x13, 1)

    if elem_type_code == 0x31:  # float32
        dtype = np.float32
    elif elem_type_code == 0x32:  # uint32
        dtype = np.uint32
    elif elem_type_code == 0x33:  # uint8
        dtype = np.uint8
    elif elem_type_code == 0x34:  # uint16
        dtype = np.uint16
    else:
        dtype = np.uint8

    dtype = np.dtype(dtype).newbyteorder('<')

    # Fallback: compute number of elements from buffer length
    num_elems = array_dict.get(0x12, len(data_bytes) // elem_sz)

    return np.frombuffer(data_bytes, dtype=dtype, count=num_elems)

def parse_scan(scan_dict):
    """Parse a Scan object from MSGPACK."""
    scan_data = scan_dict.get(0x11, {})
    result = {}

    # Arrays
    for arr_key in [0x50, 0x51, 0x52, 0x53, 0x54]:  # Theta, Phi, Dist, Rssi, Property
        if arr_key in scan_data:
            if arr_key in [0x52, 0x53]:  # DistValues and RssiValues are arrays of arrays
                nested = [parse_array(subarr) for subarr in scan_data[arr_key]]
                result[KEYWORDS[arr_key]] = nested
            else:
                result[KEYWORDS[arr_key]] = parse_array(scan_data[arr_key])
        else:
            result[KEYWORDS[arr_key]] = None

    # Simple fields
    for field_key in [0x71, 0x72, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78]:
        result[KEYWORDS[field_key]] = scan_data.get(field_key)

    return result

def receive_picoscan_segment():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Listening on {UDP_IP}:{UDP_PORT}...")

    while True:
        data, addr = sock.recvfrom(BUFFER_SIZE)

        # Check framing
        if data[:4] != b'\x02\x02\x02\x02':
            print("Invalid STX framing")
            continue

        payload_size = struct.unpack('<I', data[4:8])[0]
        payload = data[8:8+payload_size]

        crc_received = struct.unpack('<I', data[8+payload_size:12+payload_size])[0]
        crc_calculated = zlib.crc32(payload)
        if crc_received != crc_calculated:
            print(f"CRC mismatch: {crc_received} != {crc_calculated}")
            continue

        # Unpack MSGPACK
        unpacked = msgpack.unpackb(payload, strict_map_key=False)

        # Validate ScanSegment
        if unpacked.get(0x10) != SCANSEGMENT_CLASSCODE:
            print("Received non-ScanSegment packet")
            continue

        segment_data = unpacked.get(0x11, {})

        # LayerId is a simple list of ints
        layer_ids = np.array(segment_data.get(0xA0, []), dtype=np.int32)

        # SegmentData contains Scan objects
        scans = [parse_scan(scan) for scan in segment_data.get(0x96, [])]

        return layer_ids, scans

if __name__ == "__main__":
    layer_ids, scans = receive_picoscan_segment()
    print("Layer IDs:", layer_ids)
    for i, scan in enumerate(scans):
        print(f"\nScan {i}:")
        print("  ChannelTheta:", scan["ChannelTheta"])
        print("  ChannelPhi:", scan["ChannelPhi"])
        print("  DistValues:", scan["DistValues"])
        print("  RssiValues:", scan["RssiValues"])
