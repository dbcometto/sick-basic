from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.actions import ExecuteProcess
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution

from launch_ros.substitutions import FindPackageShare

from ament_index_python.packages import get_package_share_directory

import os
import yaml


def generate_launch_description():
    ld = LaunchDescription()


    #=========================# Launch Args #=========================#

    # steering_wheel_port = LaunchConfiguration("steering_wheel_port")
    # steering_wheel_port_la = DeclareLaunchArgument(
    #     "steering_wheel_port", default_value="/dev/input/event19"
    # )
    # ld.add_action(steering_wheel_port_la)

    # follower_list = LaunchConfiguration("follower_list")
    # follower_list_la = DeclareLaunchArgument(
    #     "follower_list", default_value="[1,2,3]"
    # )
    # ld.add_action(follower_list_la)



    #=========================# Sub Launches #=========================#



    # Image Generator
    imgen_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("sick_images"),
                    "launch",
                    "image_generator.launch.py",
                ]
            )
        )
    )
    ld.add_action(imgen_launch)



    # Point Processor
    pp_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution(
                    [
                        FindPackageShare("sick_images"),
                        "launch",
                        "point_processor.launch.py",
                    ]
                )
            )
        )
    ld.add_action(pp_launch)



    return ld
