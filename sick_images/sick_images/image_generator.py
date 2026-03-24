import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from rclpy.time import Time

from std_msgs.msg import Header
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

import numpy as np

class ImageGenerator(Node):

    def __init__(self):
        super().__init__('image_generator')

        self.get_logger().info("Starting up")



        # Parameters
        # Note these are controlled in the config file not here
        
        out_topic = (self.declare_parameter("out_topic","/incorrect").get_parameter_value().string_value)
        self.frame = (self.declare_parameter("frame","/incorrect").get_parameter_value().string_value)
        period = (self.declare_parameter("period",0.0).get_parameter_value().double_value)

        self.image_height = (self.declare_parameter("image_height",0).get_parameter_value().integer_value)
        self.image_width = (self.declare_parameter("image_width",0).get_parameter_value().integer_value)

        self.bridge = CvBridge()



        # Establish publisher
        self.image_publisher = self.create_publisher(Image, out_topic, 10)

        # Establish timer
        self.process_timer = self.create_timer(period,self.image_callback)

        # Log ready
        self.get_logger().info(f"Publishing fake images on {out_topic}")




    def image_callback(self):
        image = np.zeros((self.image_height, self.image_width), dtype = np.uint8)

        for i in range(self.image_height):
            for j in range(self.image_width):
                image[i,j] = np.floor((1-i/self.image_height)*(1-j/self.image_width)*255)

        header = Header()
        header.frame_id = self.frame
        header.stamp = self.get_clock().now().to_msg()

        msg = self.bridge.cv2_to_imgmsg(image,encoding="mono8",header=header)

        self.image_publisher.publish(msg)






def main(args=None):
    rclpy.init(args=args)

    node = ImageGenerator()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("Shutting down!")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()



