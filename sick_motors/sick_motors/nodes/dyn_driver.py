import rclpy
from rclpy.node import Node

import sick_motors.utils.dynamixel_sdk as dynamixel
from sick_motors.utils.dyn_xl430 import XL430W250T
import sick_motors.utils.dyn_utils as dyn_utils

from sick_interface.msg import MotorPositionCommand, MotorPositionRead

class DynDriver(Node):

    def __init__(self):
        super().__init__('dyn_driver')

        self.get_logger().info("Starting up")



        # Parameters
        # Note these are controlled in the config file not here
        
        command_topic = (
            self.declare_parameter("command_topic","/not_set")
            .get_parameter_value()
            .string_value
        )

        read_topic = (
            self.declare_parameter("read_topic","/not_set")
            .get_parameter_value()
            .string_value
        )

        driver_read_period = (
            self.declare_parameter("driver_read_period",0.0)
            .get_parameter_value()
            .double_value
        )

        port = (
            self.declare_parameter("port","not_set")
            .get_parameter_value()
            .string_value
        )

        self.id_list = (
            self.declare_parameter("id_list",[0])
            .get_parameter_value()
            .integer_array_value
        )

        self.motor_gains = (
            self.declare_parameter("motor_gains",[0,0,0])
            .get_parameter_value()
            .integer_array_value
        )

        

        # Timers, Publishers, Subscribers
        self.read_timer = self.create_timer(driver_read_period, self.read_callback)
        self.read_publisher = self.create_publisher(MotorPositionRead, read_topic, 10)
        self.command_subscriber = self.create_subscription(MotorPositionCommand, command_topic, self.command_callback, 10)


        # Set up dynamixel communication
        self.controller_port = dynamixel.PortHandler(port)
        self.packet_handler = dynamixel.PacketHandler(2.0)  # protocol version 2.0

        self.controller_port.openPort()
        self.controller_port.setBaudRate(57600)

        # Set up motors for extended position control
        for id in self.id_list:
            self.init_motor(id)


        # Log ready
        self.get_logger().info(f"Ready: tracking motors {list(self.id_list)}")




    def init_motor(self,id):
        self.packet_handler.write1ByteTxRx(self.controller_port, id, XL430W250T.ADDRESS.TORQUE_ENABLE, 0)

        # Ensure operating mode
        self.packet_handler.write1ByteTxRx(self.controller_port, id, XL430W250T.ADDRESS.OPERATING_MODE, XL430W250T.OPERATING_MODE.EXTENDED_POSITION_CONTROL)

        # Set controller gains
        self.packet_handler.write2ByteTxRx(self.controller_port, id, XL430W250T.ADDRESS.POSITION_P_GAIN, self.motor_gains[0])
        self.packet_handler.write2ByteTxRx(self.controller_port, id, XL430W250T.ADDRESS.POSITION_I_GAIN, self.motor_gains[1])
        self.packet_handler.write2ByteTxRx(self.controller_port, id, XL430W250T.ADDRESS.POSITION_D_GAIN, self.motor_gains[2])

        # Enable torque
        self.packet_handler.write1ByteTxRx(self.controller_port, id, XL430W250T.ADDRESS.TORQUE_ENABLE, 1)





    def read_callback(self):
        """Query every tracked motor for present position and publish it"""
        for id in self.id_list:
            position, error, result = self.packet_handler.read4ByteTxRx(self.controller_port, id, XL430W250T.ADDRESS.PRESENT_POSITION)
            
            if error != 0:
                self.get_logger().warn(f"Motor {id} had error {error} and read {position,error,result}")

            else:
                msg = MotorPositionRead()

                msg.header.stamp = self.get_clock().now().to_msg()
                msg.header.frame_id = ""

                msg.motor_id = id
                msg.position = dyn_utils.uint32_to_int32(position)

                self.read_publisher.publish(msg)

    def command_callback(self,cmd_msg: MotorPositionCommand):

        id = cmd_msg.motor_id

        if id not in self.id_list:
            self.get_logger().warn(f"Command sent for motor with ID {id} but not tracking that motor")

        else:
            self.packet_handler.write4ByteTxRx(self.controller_port, id, XL430W250T.ADDRESS.GOAL_POSITION, cmd_msg.goal_position)




def main(args=None):
    rclpy.init(args=args)

    node = DynDriver()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("Shutting down!")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()



