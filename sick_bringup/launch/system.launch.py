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


def load_parameters(param_file):
    with open(param_file, 'r') as file:
        return yaml.safe_load(file)

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

    params_file = "system.config.yaml"
    params = os.path.join(
        get_package_share_directory('sick_bringup'),
        "config",
        params_file)
    system_params = load_parameters(params)


    #=========================# Sub Launches #=========================#



    # Scanning
    scanning_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("sick_bringup"),
                    "launch",
                    "scan_system.launch.py",
                ]
            )
        )
    )
    ld.add_action(scanning_launch)



    # Sweeper Control
    sweeper_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution(
                    [
                        FindPackageShare("sick_bringup"),
                        "launch",
                        "sweeper_system.launch.py",
                    ]
                )
            )
        )
    ld.add_action(sweeper_launch)

    # State estimation from motors (otherwise use lidar in scan_system.launch.py)
    if system_params.get("estimate_using_motors","False") == "True":
        mount_state_estimator_launch = IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution(
                        [
                            FindPackageShare("sick_state"),
                            "launch",
                            "mount_state_estimator.launch.py",
                        ]
                    )
                )
            )
        ld.add_action(mount_state_estimator_launch)



    return ld
