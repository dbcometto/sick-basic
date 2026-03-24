import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from rclpy.time import Time

from std_msgs.msg import Header
from sensor_msgs.msg import Image, PointCloud2, PointField
import sensor_msgs_py.point_cloud2 as pc2
from cv_bridge import CvBridge
import cv2

from tf2_ros import Buffer, TransformListener
import tf2_sensor_msgs.tf2_sensor_msgs as tf2_sensor_msgs

import numpy as np

class PointProcessor(Node):
    """Colors point clouds from an image"""

    def __init__(self):
        super().__init__('point_processor')

        # Parameters
        # Note these are controlled in the config file not here
        image_topic = (self.declare_parameter("image_topic","/incorrect").get_parameter_value().string_value)
        point_cloud_topic = (self.declare_parameter("point_cloud_topic","/incorrect").get_parameter_value().string_value)
        out_topic = (self.declare_parameter("out_topic","/incorrect").get_parameter_value().string_value)
        self.in_frame = (self.declare_parameter("in_frame","/incorrect").get_parameter_value().string_value)
        self.camera_frame = (self.declare_parameter("camera_frame","/incorrect").get_parameter_value().string_value)
        process_period = (self.declare_parameter("process_period",0.0).get_parameter_value().double_value)
        self.value_name = (self.declare_parameter("value_name","incorrect").get_parameter_value().string_value)

        self.image_encoding = (self.declare_parameter("image_encoding","incorrect").get_parameter_value().string_value)
        self.image_width = (self.declare_parameter("image_width",0).get_parameter_value().integer_value)
        self.image_height = (self.declare_parameter("image_height",0).get_parameter_value().integer_value)
        self.fx = (self.declare_parameter("fx",0).get_parameter_value().integer_value)
        self.fy = (self.declare_parameter("fy",0).get_parameter_value().integer_value)
        self.cx = (self.declare_parameter("cx",0).get_parameter_value().integer_value)
        self.cy = (self.declare_parameter("cy",0).get_parameter_value().integer_value)

        tf2_buffer_size = (self.declare_parameter("tf2_buffer_size",0.0).get_parameter_value().double_value)

    
        # Establish publisher
        self.cloud_publisher = self.create_publisher(PointCloud2, out_topic, 10)

        # Establish subscriber
        self.image_subscriber = self.create_subscription(Image, image_topic, self.image_callback, 10)
        self.cloud_subscriber = self.create_subscription(PointCloud2, point_cloud_topic, self.cloud_callback, 10)

        # Establish timer
        self.process_timer = self.create_timer(process_period,self.process_callback)

        # TF setup
        self.tf_buffer = Buffer(cache_time=Duration(seconds=tf2_buffer_size))
        self.tf_listener = TransformListener(self.tf_buffer, self)



        # State
        self.bridge = CvBridge()
        self.image = None
        self.cloud = None

        # Log ready
        self.get_logger().info(f"Ready to combine {point_cloud_topic} clouds with {image_topic} images onto {out_topic}")




    def image_callback(self, msg: Image):
        """Store the most recent image message"""
        self.image = msg

    def cloud_callback(self, msg: PointCloud2):
        """Store the most recent cloud message """
        self.cloud = msg


    def process_callback(self):
        """Combine the image and pointcloud"""
        if self.cloud is None or self.image is None:
            return

        cloud_time = Time.from_msg(self.cloud.header.stamp)

        try:
            tf = self.tf_buffer.lookup_transform(
                        target_frame=self.camera_frame,          # target
                        source_frame=self.in_frame,      # source
                        time=cloud_time,     # zero or default = latest available
                        timeout=Duration(seconds=0.001)
                    )

            # Apply the transform to the PointCloud2
            transformed_cloud = tf2_sensor_msgs.do_transform_cloud(self.cloud,tf)
            points = pc2.read_points_numpy(transformed_cloud, field_names=("x","y","z","intensity"))

            if points.size==0:
                self.get_logger().warn(f"No points")
                return

            X, Y, Z = points[:,0], points[:,1], points[:,2]

            # Grab only points in front of camera
            mask_front = Z > 0
            base_indices_front = np.flatnonzero(mask_front)

            X_front, Y_front, Z_front = X[mask_front], Y[mask_front], Z[mask_front]

            # Project to pixels
            u = np.round((self.fx * X_front) / Z_front + self.cx).astype(int)
            v = np.round((self.fy * Y_front) / Z_front + self.cy).astype(int)

            # Mask inside image bounds
            img = self.bridge.imgmsg_to_cv2(self.image,desired_encoding=self.image_encoding)
            H, W = img.shape

            if H != self.image_height or W != self.image_width:
                self.get_logger().warn(f"Image width or height does not match: height {H} versus config {self.image_height} | {W} versus config {self.image_width}")

            # Get values and track indices
            mask_in_image = (u >= 0) & (u < W) & (v >= 0) & (v < H)
            indices_to_update = base_indices_front[mask_in_image]
            u_valid, v_valid = u[mask_in_image], v[mask_in_image]
            values = img[v_valid, u_valid].astype(np.float32)


            # Push values back into original array
            base_points = pc2.read_points_numpy(self.cloud, field_names=("x","y","z","intensity"))

            if base_points.shape[1] < 5: # Add columns for value/intensity if they don't exist
                base_points = np.hstack((base_points, np.zeros((base_points.shape[0],1), dtype=np.float32)))

            base_points[indices_to_update, 4] = values # update valid values

            header = self.cloud.header

            fields = [
                PointField(name='x', offset=0,  datatype=PointField.FLOAT32, count=1),
                PointField(name='y', offset=4,  datatype=PointField.FLOAT32, count=1),
                PointField(name='z', offset=8,  datatype=PointField.FLOAT32, count=1),
                PointField(name='intensity', offset=12, datatype=PointField.FLOAT32, count=1),
                PointField(name='value', offset=16, datatype=PointField.FLOAT32, count=1),
            ]

            msg = pc2.create_cloud(header, fields, base_points)
            self.cloud_publisher.publish(msg)


        except Exception as e:
            self.get_logger().warn(f"Exception processing cloud: {e}")








def main(args=None):
    rclpy.init(args=args)

    node = PointProcessor()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("Shutting down!")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()



