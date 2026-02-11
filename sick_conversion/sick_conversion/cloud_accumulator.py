import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, PointField
from sensor_msgs_py import point_cloud2

import numpy as np
from collections import deque

class CloudAccumulator(Node):

    def __init__(self):
        super().__init__('cloud_accumulator')

        self.get_logger().info("Starting up")



        # Parameters
        # Note these are controlled in the config file not here
        
        cloud_input_topic = (
            self.declare_parameter("cloud_input_topic","/incorrect")
            .get_parameter_value()
            .string_value
        )

        accum_cloud_topic = (
            self.declare_parameter("accum_cloud_topic","/incorrect")
            .get_parameter_value()
            .string_value
        )

        self.buffer_time = (
            self.declare_parameter("buffer_time",0.0)
            .get_parameter_value()
            .double_value
        )



        

        

        # Establish publisher
        self.cloud_publisher = self.create_publisher(PointCloud2, accum_cloud_topic, 10)

        # Establish subscriber
        self.scan_subscriber = self.create_subscription(PointCloud2, cloud_input_topic, self.input_callback, 10)


        # Set up
        self.buffer = deque()



        # Log ready
        self.get_logger().info(f"Ready to accumulate scans from {cloud_input_topic} into {accum_cloud_topic}")





    def input_callback(self,msg):
        try:
            time_now = self.get_clock().now().nanoseconds * 1e-9
            points = np.array(list(point_cloud2.read_points(msg,field_names=("x","y","z","intensity"), skip_nans=True)))

            # self.get_logger().info(f"shape {points.shape}, data: {points}")

            # Add to and update buffer
            self.buffer.append((time_now,points))
            while self.buffer and (time_now - self.buffer[0][0] > self.buffer_time):
                self.buffer.popleft()

            # Flatten buffer
            accum_points = []
            for _,p in self.buffer:
                accum_points.extend(p)

            # Create Message
            fields = [
                PointField(name="x",offset=0,datatype=PointField.FLOAT32,count=1),
                PointField(name="y",offset=4,datatype=PointField.FLOAT32,count=1),
                PointField(name="z",offset=8,datatype=PointField.FLOAT32,count=1),
                PointField(name="intensity",offset=12,datatype=PointField.FLOAT32,count=1),
            ]
            out_msg = point_cloud2.create_cloud(msg.header, fields, accum_points)

            # Publish
            # self.get_logger().info(f"{out_msg}")
            self.cloud_publisher.publish(out_msg)

        except Exception as e:
            self.get_logger().warn(f"Accumulation Failed: {e}")




def main(args=None):
    rclpy.init(args=args)

    node = CloudAccumulator()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("Shutting down!")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()



