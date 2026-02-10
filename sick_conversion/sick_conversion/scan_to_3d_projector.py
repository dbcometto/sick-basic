import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from rclpy.time import Time

from sensor_msgs.msg import LaserScan, PointCloud2
from laser_geometry import LaserProjection

import tf2_ros
import tf2_sensor_msgs.tf2_sensor_msgs as tf2_sensor_msgs
from collections import deque

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
            self.declare_parameter("tf2_buffer_size",0.0)
            .get_parameter_value()
            .double_value
        )

        process_period = (
            self.declare_parameter("process_period",0.0)
            .get_parameter_value()
            .double_value
        )

        self.max_scan_queue_size = (
            self.declare_parameter("max_scan_queue_size",1)
            .get_parameter_value()
            .integer_value
        )

        self.max_scan_queue_time = (
            self.declare_parameter("max_scan_queue_time",0.0)
            .get_parameter_value()
            .double_value
        )




        

        

        # Establish publisher
        self.cloud_publisher = self.create_publisher(PointCloud2, cloud_topic, 10)

        # Establish subscriber
        self.scan_subscriber = self.create_subscription(LaserScan, scan_topic, self.scan_callback, 10)

        # Establish timer
        self.process_timer = self.create_timer(process_period,self.process_callback)

        # TF2 set up
        self.tf_buffer = tf2_ros.Buffer(cache_time=Duration(seconds=tf2_buffer_size))
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # Queue setup
        self.scan_queue = deque()

        # Create projector
        self.projector = LaserProjection()


        # Log ready
        self.get_logger().info(f"Ready to move scans on {scan_topic} to clouds on {cloud_topic}")





    def scan_callback(self,msg:LaserScan):
        if len(self.scan_queue) >= self.max_scan_queue_size:
            self.scan_queue.popleft()

        self.scan_queue.append(msg)


        # try:
        #     latest_tf = self.tf_buffer.lookup_transform(
        #                     self.target_frame,    # target
        #                     msg.header.frame_id,    # source
        #                     Time(nanoseconds=0),  # zero or default = latest available
        #                     timeout=Duration(seconds=0.1)
        #     )
        #     self.get_logger().info(f"Latest is {latest_tf.header.stamp} versus {msg.header.stamp} ")
        # except Exception as e:
        #     self.get_logger().warn(f"Failed: {e} ")



    def process_callback(self):
        now = self.get_clock().now()

        while self.scan_queue:
            msg = self.scan_queue[0]
            msg_time = Time.from_msg(msg.header.stamp)

            if now - msg_time > Duration(seconds=self.max_scan_queue_time):
                self.scan_queue.popleft()

            else:
                try:
                    tf = self.tf_buffer.lookup_transform(
                        self.target_frame,          # target
                        source_frame=msg.header.frame_id,      # source
                        time=msg_time,     # zero or default = latest available
                        timeout=Duration(seconds=0.001)
                    )
                except Exception as e:
                    # self.get_logger().warn(f"Exception looking up transform: {e}")
                    break

                self.scan_queue.popleft()
                self.process_scan(msg,tf)




    def process_scan(self,msg:LaserScan,tf:tf2_ros.TransformStamped):
        try:
            # start = self.get_clock().now()
            cloud = self.projector.projectLaser(msg)
            # end = self.get_clock().now()

            # self.get_logger().info(f"Projection took {end.nanoseconds - start.nanoseconds}ns")



            # if self.tf_buffer.can_transform(
            #     self.target_frame,
            #     cloud.header.frame_id,
            #     cloud.header.stamp,
            #     timeout=rclpy.duration.Duration(seconds=2)
            #     ):

            cloud_tf = tf2_sensor_msgs.do_transform_cloud(
                cloud,
                tf
            )

            # Publish
            # self.get_logger().info(f"{out_msg}")
            self.cloud_publisher.publish(cloud_tf)

    #         else:
    #             latest_tf = self.tf_buffer.lookup_transform(
    #                 self.target_frame,    # target
    #                 cloud.header.frame_id,    # source
    #                 self.get_clock().now(),  # zero or default = latest available
    #                 timeout=Duration(seconds=0.1)
    # )
    #             self.get_logger().warn(f"Discarding scan at time {msg.header.stamp}, no TF available, latest is {latest_tf.header.stamp} ")

        except Exception as e:
            self.get_logger().warn(f"Process scan dailed: {e}")




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



