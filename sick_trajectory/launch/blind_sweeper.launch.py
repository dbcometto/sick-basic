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


    params_file = "blind_sweeper.config.yaml"
    params = os.path.join(
        get_package_share_directory('sick_trajectory'),
        "config",
        params_file)
        
    node = Node(
            package="sick_trajectory",
            executable="blind_sweeper",
            name="blind_sweeper",
            output="screen",
            parameters=[
                params
            ],)
    ld.add_action(node)


    return ld