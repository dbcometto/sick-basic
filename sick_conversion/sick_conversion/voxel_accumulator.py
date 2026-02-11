import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, PointField
from sensor_msgs_py import point_cloud2
from std_msgs.msg import Header

import numpy as np
from collections import deque


class Voxel():
    def __init__(self,p):
        self.count = 1
        self.centroid = p # p = (x,y,z,intensity)
        

    def update(self,p):
        self.count += 1
        for i,v in enumerate(p):
            self.centroid[i] = self.centroid[i] + 1/self.count*(p[i]-self.centroid[i])

    def as_tuple(self):
        return self.centroid


class VoxelMap():
    def __init__(self,resolution=1.0):
        self.resolution = resolution
        self.map = {}

    def insert_point(self,p):
        key = self.get_key(p)

        if key in self.map:
            self.map[key].update(p)
        else:
            self.map[key] = Voxel(p)


    def get_key(self,p):
        # p = (x,y,z,intensity)
        return (np.floor(p[0]/self.resolution),np.floor(p[1]/self.resolution),np.floor(p[2]/self.resolution))
    

    def as_points(self):
        return [v.as_tuple() for v in self.map.values()]
    




class VoxelAccumulator(Node):

    def __init__(self):
        super().__init__('cloud_accumulator')
        # self.get_logger().info("Starting up")


        # Parameters
        # Note these are controlled in the config file not here
        
        cloud_input_topic = (
            self.declare_parameter("cloud_input_topic","/incorrect")
            .get_parameter_value()
            .string_value
        )

        voxel_map_topic = (
            self.declare_parameter("voxel_map_topic","/incorrect")
            .get_parameter_value()
            .string_value
        )
        
        timer_period = (
            self.declare_parameter("timer_period",0.0)
            .get_parameter_value()
            .double_value
        )
        
        voxel_resolution = (
            self.declare_parameter("voxel_resolution",0.0)
            .get_parameter_value()
            .double_value
        )


        

        

        # Establish publisher
        self.cloud_publisher = self.create_publisher(PointCloud2, voxel_map_topic, 10)

        # Establish subscriber
        self.scan_subscriber = self.create_subscription(PointCloud2, cloud_input_topic, self.input_callback, 10)

        # Establish timer
        self.pub_timer = self.create_timer(timer_period,self.timer_callback)


        # Set up
        # self.buffer = deque()
        self.voxelmap = VoxelMap(voxel_resolution)
        self.frame = None

        self.fields = [
            PointField(name="x",offset=0,datatype=PointField.FLOAT32,count=1),
            PointField(name="y",offset=4,datatype=PointField.FLOAT32,count=1),
            PointField(name="z",offset=8,datatype=PointField.FLOAT32,count=1),
            PointField(name="intensity",offset=12,datatype=PointField.FLOAT32,count=1),
        ]



        # Log ready
        self.get_logger().info(f"Ready to map scans from {cloud_input_topic} into {voxel_map_topic}")





    def input_callback(self,msg:PointCloud2):
        try:
            # time_now = self.get_clock().now().nanoseconds * 1e-9
            self.frame = msg.header.frame_id

            points = list(point_cloud2.read_points(msg,field_names=("x","y","z","intensity"), skip_nans=True))
            # self.get_logger().info(f"shape {points.shape}, data: {points}")

            # Add to and update buffer
            # self.buffer.append((time_now,points))
            # while self.buffer and (time_now - self.buffer[0][0] > self.buffer_time):
            #     self.buffer.popleft()
            # 
            # # Flatten buffer
            # accum_points = []
            # for _,ps in self.buffer:
            #     accum_points.extend(ps)

            # start = self.get_clock().now()
            for p in points:
                self.voxelmap.insert_point(p)
            # end = self.get_clock().now()
            # self.get_logger().info(f"Voxel map insertion took {end.nanoseconds - start.nanoseconds}ns")

        
        except Exception as e:
            self.get_logger().warn(f"Points to voxel map failed: {e}")


    def timer_callback(self):
        try:
            # start = self.get_clock().now()
            if self.frame:
                out_header = Header()
                out_header.frame_id = self.frame
                out_header.stamp = self.get_clock().now().to_msg()  
                
        
                # Create Message
                
                out_msg = point_cloud2.create_cloud(out_header, self.fields, self.voxelmap.as_points())

                # Publish
                # self.get_logger().info(f"{out_msg}")
                self.cloud_publisher.publish(out_msg)

            # end = self.get_clock().now()
            # self.get_logger().info(f"Message publication took {end.nanoseconds - start.nanoseconds}ns")

        except Exception as e:
            self.get_logger().warn(f"Publisher failed: {e}")





def main(args=None):
    rclpy.init(args=args)

    node = VoxelAccumulator()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("Shutting down!")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()



