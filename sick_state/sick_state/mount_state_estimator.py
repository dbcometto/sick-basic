import rclpy
from rclpy.node import Node
from sick_interface.msg import MotorAngleRead
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster

import numpy as np
import math

class MountStateEstimator(Node):

    def __init__(self):
        super().__init__('mount_state_estimator')

        self.get_logger().info("Starting up")



        # Parameters
        # Note these are controlled in the config file not here
        
        motor_topic = (self.declare_parameter("motor_topic","/incorrect").get_parameter_value().string_value)

        self.yaw_motor_id = (self.declare_parameter("yaw_motor_id",0).get_parameter_value().integer_value)
        self.yaw_start_frame = (self.declare_parameter("yaw_start_frame","no_frame_set").get_parameter_value().string_value)
        self.yaw_end_frame = (self.declare_parameter("yaw_end_frame","no_frame_set").get_parameter_value().string_value)

        self.pitch_motor_id = (self.declare_parameter("pitch_motor_id",0).get_parameter_value().integer_value)
        self.pitch_start_frame = (self.declare_parameter("pitch_start_frame","no_frame_set").get_parameter_value().string_value)
        self.pitch_end_frame = (self.declare_parameter("pitch_end_frame","no_frame_set").get_parameter_value().string_value)

        do_flip_pitch = (self.declare_parameter("do_flip_pitch","not_set").get_parameter_value().string_value)
        self.pitch_direction = -1 if do_flip_pitch == "True" else 1
        

        # Establish publisher
        self.tf_broadcaster = TransformBroadcaster(self)

        # Establish subscriber
        self.motor_subscriber = self.create_subscription(MotorAngleRead, motor_topic, self.motor_callback, 10)
 

        # Log ready
        self.get_logger().info(f"Ready")



    @staticmethod
    def _create_transform(stamp, frame, child_frame, xquat = 0.0, yquat = 0.0, zquat = 0.0, wquat = 1.0, xt = 0.0, yt = 0.0, zt = 0.0):
        """Create a stamped TF message from values"""
        t = TransformStamped()

        t.header.stamp = stamp
        t.header.frame_id = frame
        t.child_frame_id = child_frame

        t.transform.translation.x = xt
        t.transform.translation.y = yt
        t.transform.translation.z = zt

        t.transform.rotation.x = xquat
        t.transform.rotation.y = yquat
        t.transform.rotation.z = zquat
        t.transform.rotation.w = wquat

        return t
    
    @staticmethod
    def euler_to_quaternion(roll, pitch, yaw):
        """Convert roll, pitch, yaw (in radians) to quaternion (x, y, z, w)"""

        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)

        w = cr * cp * cy + sr * sp * sy
        x = sr * cp * cy - cr * sp * sy
        y = cr * sp * cy + sr * cp * sy
        z = cr * cp * sy - sr * sp * cy

        return (x, y, z, w)



    def motor_callback(self, msg: MotorAngleRead):
        """Read motor angles and publish transforms"""
        try:
            
            if msg.motor_id == self.yaw_motor_id:
                qx, qy, qz, qw = self.euler_to_quaternion(0.0, 0.0, msg.position)
                t = self._create_transform(msg.header.stamp, self.yaw_start_frame, self.yaw_end_frame, qx, qy, qz, qw)

            elif msg.motor_id == self.pitch_motor_id:
                qx, qy, qz, qw = self.euler_to_quaternion(0.0, self.pitch_direction*msg.position, 0.0)
                t = self._create_transform(msg.header.stamp, self.pitch_start_frame, self.pitch_end_frame, qx, qy, qz, qw)
        
            # Publish
            # self.get_logger().info(f"{t}")
            self.tf_broadcaster.sendTransform(t)

        except Exception as e:
            self.get_logger().warn(f"Transform creation failed: {e}")






def main(args=None):
    rclpy.init(args=args)

    node = MountStateEstimator()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("Shutting down!")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()



