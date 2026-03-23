import rclpy
from rclpy.node import Node

from sick_motors.utils.dyn_xl430 import XL430W250T

from sick_interface.msg import MotorAngleCommand, MotorAngleRead

class DynAngulizer(Node):

    def __init__(self):
        super().__init__('dyn_centerer')

        self.get_logger().info("Starting up")



        # Parameters
        # Note these are controlled in the config file not here
        
        command_topic_in = (self.declare_parameter("command_topic_in","/not_set").get_parameter_value().string_value)
        command_topic_out = (self.declare_parameter("command_topic_out","/not_set").get_parameter_value().string_value)

        data_topic_in = (self.declare_parameter("data_topic_in","/not_set").get_parameter_value().string_value)
        data_topic_out = (self.declare_parameter("data_topic_out","/not_set").get_parameter_value().string_value)

        motor_ids = (self.declare_parameter("motor_ids",[0]).get_parameter_value().integer_array_value)
        motor_centers = (self.declare_parameter("motor_centers",[0]).get_parameter_value().integer_array_value)

        self.id_to_centers = {id: center*XL430W250T.ANGLE_PER_POSITION for id in motor_ids for center in motor_centers}

        

        # Timers, Publishers, Subscribers
        self.data_subscriber = self.create_subscription(MotorAngleRead, data_topic_in, self.data_callback, 10)
        self.data_publisher = self.create_publisher(MotorAngleRead, data_topic_out, 10)

        self.command_subscriber = self.create_subscription(MotorAngleCommand, command_topic_in, self.command_callback, 10)
        self.command_publisher = self.create_publisher(MotorAngleCommand, command_topic_out, 10)


        # Log ready
        self.get_logger().info(f"Ready to move {data_topic_in}->{data_topic_out} and {command_topic_in}->{command_topic_out}")




    def data_callback(self,msg: MotorAngleRead):
        """Convert integer positions to angles"""

        out_msg = MotorAngleRead()
        out_msg.header = msg.header
        out_msg.motor_id = msg.motor_id

        try:
            out_msg.position = msg.position - self.id_to_centers[msg.motor_id]
        except:
            out_msg.position = msg.position

        self.data_publisher.publish(out_msg)


    def command_callback(self, msg: MotorAngleCommand):
        """Convert angle position commands to integers"""

        out_msg = MotorAngleCommand()
        out_msg.header = msg.header
        out_msg.motor_id = msg.motor_id

        try:
            out_msg.goal_position = msg.goal_position + self.id_to_centers[msg.motor_id]
        except:
            out_msg.goal_position = msg.goal_position

        self.command_publisher.publish(out_msg)




def main(args=None):
    rclpy.init(args=args)

    node = DynAngulizer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("Shutting down!")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()



