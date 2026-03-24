import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from rclpy.time import Time

from std_msgs.msg import Header
from sensor_msgs.msg import PointCloud2, PointField
import sensor_msgs_py.point_cloud2 as pc2
from cv_bridge import CvBridge
import cv2

import numpy as np

class PointCloudGenerator(Node):

    def __init__(self):
        super().__init__('point_cloud_generator')

        self.get_logger().info("Starting up")



        # Parameters
        # Note these are controlled in the config file not here
        
        out_topic = (self.declare_parameter("out_topic","/incorrect").get_parameter_value().string_value)
        self.frame = (self.declare_parameter("frame","/incorrect").get_parameter_value().string_value)
        period = (self.declare_parameter("period",0.0).get_parameter_value().double_value)

        seed = (self.declare_parameter("seed",0).get_parameter_value().integer_value)
        self.num_points = (self.declare_parameter("num_points",0).get_parameter_value().integer_value)
        self.xmin = (self.declare_parameter("xmin",0.0).get_parameter_value().double_value)
        self.xmax = (self.declare_parameter("xmax",0.0).get_parameter_value().double_value)
        self.ymin = (self.declare_parameter("ymin",0.0).get_parameter_value().double_value)
        self.ymax = (self.declare_parameter("ymax",0.0).get_parameter_value().double_value)
        self.zmin = (self.declare_parameter("zmin",0.0).get_parameter_value().double_value)
        self.zmax = (self.declare_parameter("zmax",0.0).get_parameter_value().double_value)

        self.bridge = CvBridge()
        self.nprandom = np.random.default_rng(seed=seed)



        # Establish publisher
        self.pc_publisher = self.create_publisher(PointCloud2, out_topic, 10)

        # Establish timer
        self.process_timer = self.create_timer(period,self.pc_callback)

        # Log ready
        self.get_logger().info(f"Publishing fake point_clouds on {out_topic}")




    def pc_callback(self):
        mins = np.array([self.xmin, self.ymin, self.zmin])
        maxs = np.array([self.xmax, self.ymax, self.zmax])

        xyz = self.nprandom.uniform(mins, maxs, size=(self.num_points, 3)).astype(np.float32)
        intensity = self.nprandom.uniform(0.0, 1.0, size=(self.num_points, 1)).astype(np.float32)
        points = np.hstack((xyz, intensity))

        header = Header()
        header.frame_id = self.frame
        header.stamp = self.get_clock().now().to_msg()

        fields = [
            PointField(name='x', offset=0,  datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4,  datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8,  datatype=PointField.FLOAT32, count=1),
            PointField(name='intensity', offset=12, datatype=PointField.FLOAT32, count=1),
        ]

        msg = pc2.create_cloud(header, fields, points)
        self.pc_publisher.publish(msg)






def main(args=None):
    rclpy.init(args=args)

    node = PointCloudGenerator()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("Shutting down!")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()



