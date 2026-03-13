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

    # Static TF Transforms
    static_tf_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("sick_bringup"),
                    "launch",
                    "static_tf.launch.py",
                ]
            )
        )
    )
    ld.add_action(static_tf_launch)



    # Lidar Driver
    driver_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("sick_driver"),
                    "launch",
                    "lidar_driver.launch.py",
                ]
            )
        )
    )
    ld.add_action(driver_launch)





    # Lidar State Estimator
    lidar_state_estimator_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution(
                    [
                        FindPackageShare("sick_state"),
                        "launch",
                        "lidar_state_estimator.launch.py",
                    ]
                )
            )
        )
    ld.add_action(lidar_state_estimator_launch)



    # Scan to Cloud
    scan_to_3d_projector_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("sick_conversion"),
                    "launch",
                    "scan_to_3d_projector.launch.py",
                ]
            )
        )
    )
    ld.add_action(scan_to_3d_projector_launch)


    # Cloud Accumulation
    cloud_accumulator_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("sick_conversion"),
                    "launch",
                    "cloud_accumulator.launch.py",
                ]
            )
        )
    )
    ld.add_action(cloud_accumulator_launch)

    # Voxel Accumulation
    voxel_accumulator_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("sick_conversion"),
                    "launch",
                    "voxel_accumulator.launch.py",
                ]
            )
        )
    )
    ld.add_action(voxel_accumulator_launch)



    return ld
