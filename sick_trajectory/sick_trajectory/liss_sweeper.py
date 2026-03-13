import rclpy
from rclpy.node import Node
from sick_interface.msg import MotorAngleCommand, MotorAngleRead

import numpy as np
from enum import IntEnum

from sick_motors.utils.dyn_xl430 import XL430W250T



class LissajouSweeper(Node):

    def __init__(self):
        super().__init__('lissa_sweeper')

        self.get_logger().info("Starting up")



        # Parameters
        # Note these are controlled in the config file not here
        
        command_topic = (self.declare_parameter("command_topic","/incorrect").get_parameter_value().string_value)
        read_topic = (self.declare_parameter("read_topic","/incorrect").get_parameter_value().string_value)
        control_period = (self.declare_parameter("control_period",0.0).get_parameter_value().double_value)
        self.max_delta = (self.declare_parameter("max_delta",0.0).get_parameter_value().double_value)

        self.yaw_motor_id = (self.declare_parameter("yaw_motor_id",0).get_parameter_value().integer_value)
        yaw_center_int = (self.declare_parameter("yaw_center_int",0).get_parameter_value().integer_value)
        yaw_sweep_time = (self.declare_parameter("yaw_sweep_time",0.0).get_parameter_value().double_value)
        self.yaw_amplitude = (self.declare_parameter("yaw_amplitude",0.0).get_parameter_value().double_value)
        self.yaw_min = (self.declare_parameter("yaw_min",0.0).get_parameter_value().double_value)
        self.yaw_max = (self.declare_parameter("yaw_max",0.0).get_parameter_value().double_value)

        self.pitch_motor_id = (self.declare_parameter("pitch_motor_id",0).get_parameter_value().integer_value)
        pitch_center_int = (self.declare_parameter("pitch_center_int",0).get_parameter_value().integer_value)
        pitch_sweep_time = (self.declare_parameter("pitch_sweep_time",0.0).get_parameter_value().double_value)
        self.pitch_amplitude = (self.declare_parameter("pitch_amplitude",0.0).get_parameter_value().double_value)
        self.pitch_min = (self.declare_parameter("pitch_min",0.0).get_parameter_value().double_value)
        self.pitch_max = (self.declare_parameter("pitch_max",0.0).get_parameter_value().double_value)
        
        # Checking config
        assert control_period > 0.0
        assert yaw_sweep_time > 0.0
        assert pitch_sweep_time > 0.0

        assert self.yaw_min < self.yaw_max
        assert self.pitch_min < self.pitch_max

        assert abs(self.yaw_amplitude) <= min(abs(self.yaw_min), abs(self.yaw_max))
        assert abs(self.pitch_amplitude) <= min(abs(self.pitch_min), abs(self.pitch_max))

        # Calculations
        self.yaw_sweep_period = 2*yaw_sweep_time
        self.pitch_sweep_period = 2*pitch_sweep_time

        self.yaw_center = yaw_center_int*XL430W250T.ANGLE_PER_POSITION
        self.pitch_center = pitch_center_int*XL430W250T.ANGLE_PER_POSITION

        self.yaw_freq = 2*np.pi/self.yaw_sweep_period
        self.pitch_freq = 2*np.pi/self.pitch_sweep_period


        # Safety Values
        self.yaw_upbound = self.yaw_center+self.yaw_max
        self.yaw_lowbound = self.yaw_center+self.yaw_min

        self.pitch_upbound = self.pitch_center+self.pitch_max
        self.pitch_lowbound = self.pitch_center+self.pitch_min
        
        # Establish timer
        self.timer = self.create_timer(control_period, self.control_callback)

        # Establish Publisher
        self.command_publisher = self.create_publisher(MotorAngleCommand, command_topic, 10)

        # Establish subscriber
        self.angle_subscriber = self.create_subscription(MotorAngleRead, read_topic, self.read_angle, 10)

        # Set state
        self.start_time = self.get_clock().now()

        self.current_state = {
            self.yaw_motor_id: None,
            self.pitch_motor_id: None,
        }

        # Log ready
        self.get_logger().info(f"Ready to sweep Motor {self.yaw_motor_id} for yaw and Motor {self.pitch_motor_id} for pitch")


    def publish_motor_command(self,id,position):
        """Publish a command message given an id and a goal position"""
        out_msg = MotorAngleCommand()
        out_msg.header.stamp = self.get_clock().now().to_msg()
        out_msg.motor_id = id

        out_msg.goal_position = position

        self.command_publisher.publish(out_msg)


    def read_angle(self,msg: MotorAngleRead):
        """Update the current state based on read angle"""
        self.current_state[msg.motor_id] = msg.position


    def control_callback(self):
        """On a timer, control the system to follow a trajectory"""

        if all([s is not None for s in self.current_state.values()]):
            current_time = (self.get_clock().now() - self.start_time).nanoseconds * 1e-9

            new_yaw_goal = self.yaw_amplitude*np.sin(self.yaw_freq*current_time)
            new_pitch_goal = self.pitch_amplitude*np.sin(self.pitch_freq*current_time)
            
            centered_yaw_goal = self.yaw_center+new_yaw_goal
            centered_pitch_goal = self.pitch_center+new_pitch_goal

            yaw_command = np.clip(centered_yaw_goal,self.yaw_lowbound,self.yaw_upbound)           
            pitch_command = np.clip(centered_pitch_goal,self.pitch_lowbound,self.pitch_upbound)

            safe_yaw_command = np.clip(yaw_command, self.current_state[self.yaw_motor_id]-self.max_delta, self.current_state[self.yaw_motor_id]+self.max_delta)
            safe_pitch_command = np.clip(pitch_command, self.current_state[self.pitch_motor_id]-self.max_delta, self.current_state[self.pitch_motor_id]+self.max_delta)
            
            self.publish_motor_command(self.yaw_motor_id,safe_yaw_command)
            self.publish_motor_command(self.pitch_motor_id,safe_pitch_command)

    
    def shutdown(self):
        """Runs on shutdown"""
        # self.get_logger().info(f"Zeroing and shutting down")
        # self.publish_motor_command(self.yaw_motor_id,self.yaw_center)
        # self.publish_motor_command(self.pitch_motor_id,self.pitch_center)
        pass






def main(args=None):
    rclpy.init(args=args)

    node = LissajouSweeper()

    try:
        rclpy.spin(node)
    except Exception as e:
        pass
    finally:
        print("Shutting down!")
        node.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()



