import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster

import socket
import msgpack
import numpy as np

class LidarStateEstimator(Node):

    def __init__(self):
        super().__init__('lidar_state_estimator')

        self.get_logger().info("Starting up")



        # Parameters
        # Note these are controlled in the config file not here
        
        imu_topic = (
            self.declare_parameter("imu_topic","/incorrect")
            .get_parameter_value()
            .string_value
        )

        self.frame = (
            self.declare_parameter("frame","no_frame_set")
            .get_parameter_value()
            .string_value
        )

        self.child_frame = (
            self.declare_parameter("child_frame","no_frame_set")
            .get_parameter_value()
            .string_value
        )

        

        # Establish publisher
        self.tf_broadcaster = TransformBroadcaster(self)

        # Establish subscriber
        self.imu_subscriber = self.create_subscription(Imu, imu_topic, self.imu_callback, 10)

 

        # Log ready
        self.get_logger().info(f"Ready")





    def imu_callback(self,msg:Imu):
        try:
            t = TransformStamped()

            t.header.stamp = msg.header.stamp
            t.header.frame_id = self.frame
            t.child_frame_id = self.child_frame

            t.transform.translation.x = 0.0
            t.transform.translation.y = 0.0
            t.transform.translation.z = 0.0

            t.transform.rotation.x = msg.orientation.x
            t.transform.rotation.y = msg.orientation.y
            t.transform.rotation.z = msg.orientation.z
            t.transform.rotation.w = msg.orientation.w
        
            # Publish
            # self.get_logger().info(f"{t}")
            self.tf_broadcaster.sendTransform(t)

        except Exception as e:
            self.get_logger().warn(f"Transform creation failed: {e}")






def main(args=None):
    rclpy.init(args=args)

    node = LidarStateEstimator()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("Shutting down!")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()



