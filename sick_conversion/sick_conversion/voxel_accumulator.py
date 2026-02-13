import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, PointField
from sensor_msgs_py import point_cloud2
from std_msgs.msg import Header

import numpy as np
import random
import math
from collections import deque


class Voxel():
    def __init__(self,p):
        self.count = 1
        self.centroid = p # p = (x,y,z,intensity)
        self.freecount = 0
        

    def update(self,p):
        self.count += 1
        for i,v in enumerate(p):
            self.centroid[i] = self.centroid[i] + 1/self.count*(p[i]-self.centroid[i])

    def free_update(self,ratio=None):
        self.freecount += 1

        if ratio:
            return self.should_delete(ratio)

    def should_delete(self,ratio):
        return True if self.freecount > ratio*self.count else False

    def as_tuple(self):
        return self.centroid




class VoxelMap():
    def __init__(self,resolution=1.0,percent_clearance=1.0,cleanup_ratio=3.0,seed=None):
        self.resolution = resolution
        self.percent_clearance = percent_clearance
        self.cleanup_ratio = cleanup_ratio

        if seed:
            random.seed(seed)

        self.map = {}

    def update_map_with_point(self,p,origin=(0,0,0,0)):
        # First handle clearing
        if random.random() <= self.percent_clearance:
            for k in self.trace_ray(p,origin):
                if self.map[k].free_update(self.cleanup_ratio): # returns flag about whether voxel should be deleted
                    self.delete_voxel(k)

        # Then add
        self.insert_point(p)



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
    

    def delete_voxel(self,key):
        del self.map[key]


    def trace_ray(self,p,origin,epsilon=1e-20):
        # Setup
        x0 = [origin[0],origin[1],origin[2]]
        x1 = [p[0],p[1],p[2]]

        # Start and end keys
        key0 = self.get_key(origin)
        key1 = self.get_key(p)

        # Direction & time between grids & starting time of next grid
        delta = [0,0,0]
        step = [0,0,0]
        tDelta = [0,0,0]
        tNext = [0,0,0]
        for axis in range(3):
            delta[axis] = x1[axis]-x0[axis]
            step[axis] = 1 if delta[axis] > 0 else -1
            tDelta[axis] = self.resolution/abs(delta[axis])
            if tDelta[axis]==0:
                tDelta[axis] = 1e-20

            if step[axis] > 0:
                next_grid = (key0[axis]+1)*self.resolution # Forward to next voxel
            else:
                next_grid = (key0[axis])*self.resolution # Backwards to same voxel

            tNext[axis] = (next_grid - x0[axis]) / delta[axis] 

            

        # Make list of visited voxels
        keylist = []
        key = key0
        while not key==key1:
            # print(f"{type(key)} - {key} | {type(key1)} - {key1}")
            if key in self.map:
                keylist.append(key)     # Appends before stepping to ensure we don't append the last key
            
            # Find next grid crossing
            axis = 0
            if tNext[1] < tNext[axis]:
                axis = 1
            if tNext[2] < tNext[axis]:
                axis = 2

            # update to that voxel
            if axis == 0:
                key = (key[0] + step[0], key[1], key[2])
            elif axis == 1:
                key = (key[0], key[1] + step[1], key[2])
            else:
                key = (key[0], key[1], key[2] + step[2])

            # Update next collisions
            tNext[axis] += tDelta[axis]


        
        return keylist
    


    # def trace_ray(self,p,origin):  # Old vectorized clean version
    #     # Setup
    #     x0 = np.array([origin[0],origin[1],origin[2]])
    #     x1 = np.array([p[0],p[1],p[2]])

    #     # Start and end keys
    #     key0 = self.get_key(origin)
    #     key1 = self.get_key(p)

    #     # Direction
    #     delta = x1-x0
    #     delta = np.where(delta==0,1e-20,delta)
    #     step = np.sign(delta).astype(int)

    #     # Time between gridpoints
    #     tDelta = self.resolution/np.abs(delta)

    #     # Time of next grid intersection
    #     tNext = np.zeros((3,1))
    #     for axis in range(3):
    #         if step[axis] > 0:
    #             next_grid = (key0[axis]+1)*self.resolution # Forward to next voxel
    #         else:
    #             next_grid = (key0[axis])*self.resolution # Backwards to same voxel

    #         tNext[axis] = (next_grid - x0[axis]) / delta[axis] 

    #     # Make list of visited voxels
    #     keylist = []
    #     key = [key0[0],key0[1],key0[2]]
    #     last_key = list(key1)
    #     while not key==last_key:
    #         keylist.append(tuple(key))     # Appends before stepping to ensure we don't append the last key
    #         axis = np.argmin(tNext)
    #         key[axis] += step[axis]
    #         tNext[axis] += tDelta[axis]
        
    #     return keylist




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

        percent_clearance = (
            self.declare_parameter("percent_clearance",0.0)
            .get_parameter_value()
            .double_value
        )

        cleanup_ratio = (
            self.declare_parameter("cleanup_ratio",0.0)
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
        self.voxelmap = VoxelMap(voxel_resolution,percent_clearance,cleanup_ratio)
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



            # start = self.get_clock().now()
            for p in points:
                self.voxelmap.update_map_with_point(p)
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



