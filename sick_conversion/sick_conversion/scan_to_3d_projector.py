import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from rclpy.time import Time

from sensor_msgs.msg import LaserScan, PointCloud2
from laser_geometry import LaserProjection

import tf2_ros
import tf2_sensor_msgs.tf2_sensor_msgs as tf2_sensor_msgs

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

        self.target_frame = (
            self.declare_parameter("target_frame","no_frame_set")
            .get_parameter_value()
            .string_value
        )

        tf2_buffer_size = (
            self.declare_parameter("tf2_buffer_size",1.0)
            .get_parameter_value()
            .double_value
        )




        

        

        # Establish publisher
        self.cloud_publisher = self.create_publisher(PointCloud2, cloud_topic, 10)

        # Establish subscriber
        self.scan_subscriber = self.create_subscription(LaserScan, scan_topic, self.scan_callback, 10)

        # TF2 set up
        self.tf_buffer = tf2_ros.Buffer(cache_time=Duration(seconds=tf2_buffer_size))
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # Create projector
        self.projector = LaserProjection()


        # Log ready
        self.get_logger().info(f"Ready to move scans on {scan_topic} to clouds on {cloud_topic}")





    def scan_callback(self,msg:LaserScan):
        try:
            latest_tf = self.tf_buffer.lookup_transform(
                            self.target_frame,    # target
                            msg.header.frame_id,    # source
                            Time(nanoseconds=0),  # zero or default = latest available
                            timeout=Duration(seconds=0.1)
            )
            self.get_logger().info(f"Latest is {latest_tf.header.stamp} versus {msg.header.stamp} ")
        except Exception as e:
            self.get_logger().warn(f"Failed: {e} ")

    #     try:
    #         start = self.get_clock().now()
    #         cloud = self.projector.projectLaser(msg)
    #         end = self.get_clock().now()

    #         self.get_logger().info(f"Projection took {end.nanoseconds - start.nanoseconds}ns")



    #         # if self.tf_buffer.can_transform(
    #         #     self.target_frame,
    #         #     cloud.header.frame_id,
    #         #     cloud.header.stamp,
    #         #     timeout=rclpy.duration.Duration(seconds=2)
    #         #     ):

    #         cloud_tf = tf2_sensor_msgs.do_transform_cloud(
    #             cloud,
    #             self.tf_buffer.lookup_transform(
    #                 self.target_frame,                 # target
    #                 cloud.header.frame_id,             # source
    #                 Time(nanoseconds=0), #cloud.header.stamp, # TODO: Fix the timing issue
    #                 timeout=rclpy.duration.Duration(seconds=0.1) # TODO: fix the timing issue
    #             )
    #         )

    #         # Publish
    #         # self.get_logger().info(f"{out_msg}")
    #         self.cloud_publisher.publish(cloud_tf)

    # #         else:
    # #             latest_tf = self.tf_buffer.lookup_transform(
    # #                 self.target_frame,    # target
    # #                 cloud.header.frame_id,    # source
    # #                 self.get_clock().now(),  # zero or default = latest available
    # #                 timeout=Duration(seconds=0.1)
    # # )
    # #             self.get_logger().warn(f"Discarding scan at time {msg.header.stamp}, no TF available, latest is {latest_tf.header.stamp} ")

    #     except Exception as e:
    #         self.get_logger().warn(f"Projection/TF Failed: {e}")




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



