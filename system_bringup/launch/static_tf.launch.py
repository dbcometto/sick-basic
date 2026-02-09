import os
from launch import LaunchDescription
from ament_index_python import get_package_share_directory
from launch_ros.actions import Node
from launch.actions import  DeclareLaunchArgument, TimerAction
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    ld = LaunchDescription()

    #=============== Launch Arguments & Config ===============#

    # follower_list = LaunchConfiguration("follower_list")
    # follower_list_la = DeclareLaunchArgument(
    #     "follower_list", default_value="[1,2,3]"
    # )
    # ld.add_action(follower_list_la)


    # params_file = "lidar_config.yaml"
    # params = os.path.join(
    #     get_package_share_directory('sick_driver'),
    #     "config",
    #     params_file)
        
    map_transform_node = Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments = ['0', '0', '0', '0', '0', '0', 'world', 'map']
    )
    ld.add_action(map_transform_node)
    
    odom_transform_node = Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments = ['0', '0', '0', '0', '0', '0', 'map', 'odom']
    )
    ld.add_action(odom_transform_node)
    
    base_transform_node = Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments = ['0', '0', '0', '0', '0', '0', 'odom', 'base']
    )
    ld.add_action(base_transform_node)
    
    lidar_base_transform_node = Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments = ['0', '0', '0', '0', '0', '0', 'base', 'lidar_base']
    )
    ld.add_action(lidar_base_transform_node)


    return ld