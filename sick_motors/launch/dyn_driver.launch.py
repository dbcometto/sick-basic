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


    params_file = "lidar_driver.config.yaml"
    params = os.path.join(
        get_package_share_directory('sick_driver'),
        "config",
        params_file)
        
    driver_node = Node(
            package="sick_driver",
            executable="lidar_driver",
            name="lidar_driver",
            output="screen",
            parameters=[
                params
            ],)
    ld.add_action(driver_node)


    return ld