import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, PointCloud2
from laser_geometry import LaserProjection

import numpy as np

class ScanToCloud(Node):

    def __init__(self):
        super().__init__('scan_to_cloud_converter')

        self.get_logger().info("Starting up")



        # Parameters
        # Note these are controlled in the config file not here
        
        scan_topic = (
            self.declare_parameter("scan_topic","/incorrect")
            .get_parameter_value()
            .string_value
        )

        cloud_topic = (
            self.declare_parameter("cloud_topic","/incorrect")
            .get_parameter_value()
            .string_value
        )



        

        

        # Establish publisher
        self.cloud_publisher = self.create_publisher(PointCloud2, cloud_topic, 10)

        # Establish subscriber
        self.scan_subscriber = self.create_subscription(LaserScan, scan_topic, self.scan_callback, 10)



        # Create projector
        self.projector = LaserProjection()


        # Log ready
        self.get_logger().info(f"Ready to move scans on {scan_topic} to clouds on {cloud_topic}")





    def scan_callback(self,msg):
        try:
            out_msg = self.projector.projectLaser(msg)

            # Publish
            # self.get_logger().info(f"{out_msg}")
            self.cloud_publisher.publish(out_msg)

        except Exception as e:
            self.get_logger().warn(f"Projection Failed: {e}")




def main(args=None):
    rclpy.init(args=args)

    node = ScanToCloud()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("Shutting down!")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()



