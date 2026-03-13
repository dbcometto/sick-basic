import rclpy
from rclpy.node import Node
from sick_interface.msg import MotorAngleCommand

import numpy as np
from enum import IntEnum

from sick_motors.utils.dyn_xl430 import XL430W250T


class motor_direction(IntEnum):
    FORWARD = 1
    BACKWARD = -1


class BlindSweeper(Node):

    def __init__(self):
        super().__init__('blind_sweeper')

        self.get_logger().info("Starting up")



        # Parameters
        # Note these are controlled in the config file not here
        
        command_topic = (self.declare_parameter("command_topic","/incorrect").get_parameter_value().string_value)

        self.control_period = (self.declare_parameter("control_period",0.0).get_parameter_value().double_value)

        self.yaw_motor_id = (self.declare_parameter("yaw_motor_id",0).get_parameter_value().integer_value)
        self.yaw_center_int = (self.declare_parameter("yaw_center_int",0).get_parameter_value().integer_value)
        self.yaw_sweep_period = (self.declare_parameter("yaw_sweep_period",0.0).get_parameter_value().double_value)
        self.yaw_min = (self.declare_parameter("yaw_min",0.0).get_parameter_value().double_value)
        self.yaw_max = (self.declare_parameter("yaw_max",0.0).get_parameter_value().double_value)

        self.pitch_motor_id = (self.declare_parameter("pitch_motor_id",0).get_parameter_value().integer_value)
        self.pitch_center_int = (self.declare_parameter("pitch_center_int",0).get_parameter_value().integer_value)
        self.pitch_sweep_period = (self.declare_parameter("pitch_sweep_period",0.0).get_parameter_value().double_value)
        self.pitch_min = (self.declare_parameter("pitch_min",0.0).get_parameter_value().double_value)
        self.pitch_max = (self.declare_parameter("pitch_max",0.0).get_parameter_value().double_value)
        
        # TODO: add asserts to protect config
        assert self.control_period > 0.0
        assert self.yaw_min < self.yaw_max
        assert self.pitch_min < self.pitch_max

        # Calculations
        yaw_period_steps = int(self.yaw_sweep_period/self.control_period)
        pitch_period_steps = int(self.pitch_sweep_period/self.control_period)

        self.yaw_angle_per_step = (self.yaw_max-self.yaw_min)/yaw_period_steps
        self.pitch_angle_per_step = (self.pitch_max-self.pitch_min)/pitch_period_steps

        self.yaw_center = self.yaw_center_int*XL430W250T.ANGLE_PER_POSITION
        self.pitch_center = self.pitch_center_int*XL430W250T.ANGLE_PER_POSITION

        self.yaw_upbound = self.yaw_center+self.yaw_max
        self.yaw_lowbound = self.yaw_center+self.yaw_min

        self.pitch_upbound = self.pitch_center+self.pitch_max
        self.pitch_lowbound = self.pitch_center+self.pitch_min
        

        # Establish timer
        self.timer = self.create_timer(self.control_period, self.control_callback)

        # Establish subscriber
        self.command_publisher = self.create_publisher(MotorAngleCommand, command_topic, 10)

        # Set state
        self.current_yaw = 0.0 # These are offset from center
        self.current_pitch = 0.0

        self.yaw_direction = motor_direction.FORWARD
        self.pitch_direction = motor_direction.BACKWARD


        

        

        # Set to 0
        self.publish_motor_command(self.yaw_motor_id,self.yaw_center)
        self.publish_motor_command(self.pitch_motor_id,self.pitch_center)

        # Log ready
        self.get_logger().info(f"Ready to sweep Motor 1 and Motor 2")


    def publish_motor_command(self,id,position):
        out_msg = MotorAngleCommand()
        out_msg.header.stamp = self.get_clock().now().to_msg()
        out_msg.motor_id = id

        out_msg.goal_position = position

        self.command_publisher.publish(out_msg)


    def control_callback(self):
        
        new_yaw_goal = self.current_yaw + self.yaw_direction*self.yaw_angle_per_step
        new_pitch_goal = self.current_pitch + self.pitch_direction*self.pitch_angle_per_step

        if new_yaw_goal >= self.yaw_max:
            new_yaw_goal = self.yaw_max
            self.yaw_direction = motor_direction.BACKWARD
        elif new_yaw_goal <= self.yaw_min:
            new_yaw_goal = self.yaw_min
            self.yaw_direction = motor_direction.FORWARD
        
        if new_pitch_goal >= self.pitch_max:
            new_pitch_goal = self.pitch_max
            self.pitch_direction = motor_direction.BACKWARD
        elif new_pitch_goal <= self.pitch_min:
            new_pitch_goal = self.pitch_min
            self.pitch_direction = motor_direction.FORWARD
        
        centered_yaw_goal = self.yaw_center+new_yaw_goal
        yaw_command = np.clip(centered_yaw_goal,self.yaw_lowbound,self.yaw_upbound)

        centered_pitch_goal = self.pitch_center+new_pitch_goal
        pitch_command = np.clip(centered_pitch_goal,self.pitch_lowbound,self.pitch_upbound)
        

        self.publish_motor_command(self.yaw_motor_id,yaw_command)
        self.publish_motor_command(self.pitch_motor_id,pitch_command)

        self.current_yaw = new_yaw_goal
        self.current_pitch = new_pitch_goal

    
    def shutdown(self):
        self.get_logger().info(f"Zeroing and shutting down")
        self.publish_motor_command(self.yaw_motor_id,0.0)
        self.publish_motor_command(self.pitch_motor_id,0.0)






def main(args=None):
    rclpy.init(args=args)

    node = BlindSweeper()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.shutdown()
        print("Shutting down!")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()



