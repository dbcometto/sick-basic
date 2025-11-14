import os
from launch import LaunchDescription
from ament_index_python import get_package_share_directory
from launch_ros.actions import Node
from launch.actions import  DeclareLaunchArgument, TimerAction
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    
    # params_file = "publishing.yaml"
    # params = os.path.join(
    #     get_package_share_directory('ros_g29_force_feedback'),
    #     "config",
    #     params_file)
        
    ts_node = Node(
            package="convoy_tap",
            executable="ts_pub",
            name="ts_pub",
            output="screen",)
    
    delayed_node = TimerAction(
        period=3.0,
        actions=[ts_node]
    )

    return LaunchDescription([
        delayed_node
    ])