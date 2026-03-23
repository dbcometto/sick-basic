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
        
    map = Node(
            package='tf2_ros',
            namespace='tf',
            executable='static_transform_publisher',
            arguments = ['0', '0', '0', '0', '0', '0', 'world', 'map']
    )
    ld.add_action(map)
    
    odom = Node(
            package='tf2_ros',
            namespace='tf',
            executable='static_transform_publisher',
            arguments = ['0', '0', '0', '0', '0', '0', 'map', 'odom']
    )
    ld.add_action(odom)
    
    base = Node(
            package='tf2_ros',
            namespace='tf',
            executable='static_transform_publisher',
            arguments = ['0', '0', '0', '0', '0', '0', 'odom', 'base']
    )
    ld.add_action(base)
    
    mount_base = Node(
            package='tf2_ros',
            namespace='tf',
            executable='static_transform_publisher',
            arguments = ['0', '0', '0', '0', '0', '0', 'base', 'mount_base']
    )
    ld.add_action(mount_base)

    yaw_motor_base = Node(
            package='tf2_ros',
            namespace='tf',
            executable='static_transform_publisher',
            arguments = ['0', '0', '0', '0', '0', '0', 'mount_base', 'yaw_motor_base']
    )
    ld.add_action(yaw_motor_base)

    yaw_motor_start = Node(
            package='tf2_ros',
            namespace='tf',
            executable='static_transform_publisher',
            arguments = ['0', '0', '0.035', '0', '0', '0', 'yaw_motor_base', 'yaw_motor_start']
    )
    ld.add_action(yaw_motor_start)

    pitch_motor_base = Node(
            package='tf2_ros',
            namespace='tf',
            executable='static_transform_publisher',
            arguments = ['0', '0', '0', '0', '0', '0', 'yaw_motor_end', 'pitch_motor_base']
    )
    ld.add_action(pitch_motor_base)

    pitch_motor_start = Node(
            package='tf2_ros',
            namespace='tf',
            executable='static_transform_publisher',
            arguments = ['0', '0', '0.04', '0', '0', '0', 'pitch_motor_base', 'pitch_motor_start']
    )
    ld.add_action(pitch_motor_start)

    lidar_base = Node(
            package='tf2_ros',
            namespace='tf',
            executable='static_transform_publisher',
            arguments = ['0', '0', '0.02', '0', '0', '0', 'pitch_motor_end', 'lidar_base']
    )
    ld.add_action(lidar_base)

    lidar_sensor = Node(
            package='tf2_ros',
            namespace='tf',
            executable='static_transform_publisher',
            arguments = ['-0.01', '0', '0.07', '0', '0', '0', 'lidar_base', 'lidar_sensor']
    )
    ld.add_action(lidar_sensor)


    return ld