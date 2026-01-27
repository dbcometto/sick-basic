import rclpy
from rclpy.node import Node
from sensor_msgs.msg import MultiEchoLaserScan,LaserEcho,LaserScan,Imu

import socket
import msgpack
import numpy as np

class LidarDriver(Node):

    def __init__(self):
        super().__init__('lidar_driver')

        self.get_logger().info("Starting up")



        # Parameters
        # Note these are controlled in the config file not here
        
        scan_topic = (
            self.declare_parameter("scan_topic","/scan")
            .get_parameter_value()
            .string_value
        )

        imu_topic = (
            self.declare_parameter("imu_topic","/imu")
            .get_parameter_value()
            .string_value
        )

        driver_period = (
            self.declare_parameter("driver_period",0.005)
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
            self.declare_parameter("hostname","192.168.0.202")
            .get_parameter_value()
            .string_value
        )

        scan_port = (
            self.declare_parameter("scan_port",2115)
            .get_parameter_value()
            .integer_value
        )

        imu_port = (
            self.declare_parameter("imu_port",7503)
            .get_parameter_value()
            .integer_value
        )

        

        # Establish timer
        self.timer = self.create_timer(driver_period, self.timer_callback)

        # Establish publishers
        self.scan_publisher = self.create_publisher(LaserScan, scan_topic, 10)
        self.imu_publisher = self.create_publisher(Imu, imu_topic, 10)

        

        # Set up sockets
        self.scan_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.scan_socket.bind((hostname, scan_port))
        self.scan_socket.setblocking(False)

        self.imu_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.imu_socket.bind((hostname, imu_port))
        self.imu_socket.setblocking(False)


        # Log ready
        self.get_logger().info(f"Ready: listening for lidar on {hostname}:{scan_port} and to the IMU on {hostname}:{imu_port}")





    def timer_callback(self):

        # Receive Lidar Data
        data = None
        try:
            data, addr = self.scan_socket.recvfrom(65565)
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

            # self.get_logger().info(f"{type(np.mean(np.abs(np.diff(thetas))))}: {np.mean(np.abs(np.diff(thetas)))}")


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
            # self.get_logger().info(f"{out_msg}")
            self.scan_publisher.publish(out_msg)




    

        # Receive IMU data
        data = None
        try:
            data, addr = self.imu_socket.recvfrom(65565)
        except:
            pass

        if data:
            
            # Gather data
            values = [float(x) for x in np.frombuffer(data[3*4:13*4],dtype=np.float32)]
            timestamp = np.frombuffer(data[13*4:15*4],dtype=np.uint64)[0]
            
            
            # Create Message
            imu_msg = Imu()
            imu_msg.header.frame_id = 'lidar'
            imu_msg.header.stamp.sec = int(timestamp // 1e6)
            imu_msg.header.stamp.nanosec = int(timestamp % 1e6 )

            imu_msg.orientation.x = values[7]
            imu_msg.orientation.y = values[8]
            imu_msg.orientation.z = values[9]
            imu_msg.orientation.w = values[6]

            imu_msg.angular_velocity.x = values[3]
            imu_msg.angular_velocity.y = values[4]
            imu_msg.angular_velocity.z = values[5]

            imu_msg.linear_acceleration.x = values[0]
            imu_msg.linear_acceleration.y = values[1]
            imu_msg.linear_acceleration.z = values[2]

            
            # Publish
            # self.get_logger().info(f"{imu_msg}")
            self.imu_publisher.publish(imu_msg)



            # Debugging prints
            # self.get_logger().info(f"{data}")
            # self.get_logger().info(f"{data[3*4:4*4]}")

            # self.get_logger().info(f"ax: {values[0]:02.2f}, ay: {values[1]:02.2f}, az: {values[2]:02.2f}")
            # self.get_logger().info(f"wx: {values[3]:02.2f}, wy: {values[4]:02.2f}, wz: {values[5]:02.2f}")
            # self.get_logger().info(f"qw: {values[6]:02.2f}, qx: {values[7]:02.2f}, qy: {values[8]:02.2f}, qz: {values[9]:02.2f}")

            # self.get_logger().info(f"time: {timestamp}")
            # self.get_logger().info(f"ros time: {self.get_clock().now()}")




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



