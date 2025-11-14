import rclpy
from rclpy.node import Node
from sensor_msgs.msg import MultiEchoLaserScan,LaserEcho,LaserScan

import socket
import msgpack
import numpy as np

class LidarDriver(Node):

    def __init__(self):
        super().__init__('lidar_driver')

        self.get_logger().info("Starting up")

        output_topic = (
            self.declare_parameter("output_topic","/scan_data")
            .get_parameter_value()
            .string_value
        )

        driver_period = (
            self.declare_parameter("driver_freq",0.005)
            .get_parameter_value()
            .double_value
        )

        self.lidar_freq = (
            self.declare_parameter("lidar_freq",20.0)
            .get_parameter_value()
            .double_value
        )

        self.min_range = (
            self.declare_parameter("min_range",0.05)
            .get_parameter_value()
            .double_value
        )

        self.max_range = (
            self.declare_parameter("max_range",45)
            .get_parameter_value()
            .double_value
        )

        hostname = (
            self.declare_parameter("hostname","192.168.0.111")
            .get_parameter_value()
            .string_value
        )

        port = (
            self.declare_parameter("port",2115)
            .get_parameter_value()
            .integer_value
        )

        

        # Establish timer
        self.timer = self.create_timer(driver_period, self.timer_callback)

        # Establish publisher & Subscriber
        self.publisher = self.create_publisher(LaserScan, output_topic, 10)

        

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((hostname, port))
        self.socket.setblocking(False)
        
        self.get_logger().info(f"Listening on {hostname}:{port}")





    def timer_callback(self):
        # self.get_logger().info(f"Recv Data: {msg}")
        data = None
        try:
            data, addr = self.socket.recvfrom(65565)
        except:
            pass

        if data:
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

            # print(f"{type(np.mean(np.abs(np.diff(thetas))))}: {np.mean(np.abs(np.diff(thetas)))}")


            # Create message
            # timestamp = self.get_clock().now().to_msg()
            out_msg = LaserScan()
            out_msg.header.frame_id = "lidar"
            out_msg.header.stamp.sec = int(start_time // 1e6)
            out_msg.header.stamp.nanosec = int(start_time % 1e6)

            out_msg.angle_min = angle_min
            out_msg.angle_max = angle_max
            out_msg.angle_increment = float(np.mean(np.abs(np.diff(thetas))))
            out_msg.time_increment = (start_time-stop_time)/num_beams/1e6 # from us to s
            out_msg.scan_time = 1/self.lidar_freq
            out_msg.range_min = self.min_range
            out_msg.range_max = self.max_range


            # For laser scan
            out_msg.ranges = [float(x/1000) for x in distances[0]]
            out_msg.intensities = [float(x) for x in rssis[0]]
        


            # for multi echo laser scan
            # for dist,rssi in zip(distances,rssis):
            #     range_msg = LaserEcho()
            #     intensity_msg = LaserEcho()

            #     dist_m = dist/1000 #mm to m

            #     range_msg.echoes = [float(x) for x in dist_m.ravel()]
            #     intensity_msg.echoes = [float(x) for x in rssi]

            #     out_msg.ranges.append(range_msg)
            #     out_msg.intensities.append(intensity_msg)
        


            # Publish
            # self.get_logger().info(f"LPF Signals: {output} {self.memory}")
            self.publisher.publish(out_msg)
            






def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = LidarDriver()

    try:
        rclpy.spin(minimal_publisher)
    except KeyboardInterrupt:
        print("Shutting down!")

    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()



