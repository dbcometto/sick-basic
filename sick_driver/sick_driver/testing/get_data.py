import socket
import msgpack
import numpy as np

HOST = "192.168.0.111"
PORT = 2115


lidar_freq = 20
range_min = 0.05
range_max = 45

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))
    print(f"Listening on {HOST}:{PORT}")

    while True:
        data, addr = s.recvfrom(65565)

        # First, strip off overhead and unpack data

        packed_data = data[8:-4]
        unpacked_data = msgpack.unpackb(packed_data,strict_map_key=False)



        # Next, Grab data
        segmentData = unpacked_data[17][150]
        scanData = segmentData[0][17]

        

        start_time = scanData[113]
        stop_time = scanData[114]
        angle_min = scanData[115]
        angle_max = scanData[116]

        num_beams = scanData[119]
        num_echos = scanData[120]

        thetas = np.frombuffer(scanData[80][17],dtype=np.float32)
        distances = [np.frombuffer(x[17],dtype=np.float32,) for x in scanData[82]]
        rssis = [np.frombuffer(x[17],dtype=np.float32,) for x in scanData[83]]

        


        # Calculate ROS message values
        header_time = start_time

        angle_min = angle_min
        angle_max = angle_max
        angle_increment = np.mean(np.abs(np.diff(thetas)))

        time_increment = (start_time-stop_time)/num_beams
        scan_time = 1/lidar_freq

        ranges = distances[0]/1000 # strongest_return, mm to m
        range_min = range_min
        range_max = range_max

        intensities = rssis[0]

        print(f"{ranges.ravel()}")
        # print(" ".join(f"{b:02X}" for b in unpacked_data))
        break  # stop after first packet
