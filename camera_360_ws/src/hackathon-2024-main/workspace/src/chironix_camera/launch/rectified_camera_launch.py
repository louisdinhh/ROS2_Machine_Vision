from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory
from os.path import join

from cv2 import FileStorage, FILE_STORAGE_READ
from tf_transformations import (
    euler_from_matrix,
    translation_from_matrix,
    euler_matrix,
    inverse_matrix
)
from math import pi
from numpy import dot, linalg

def generate_launch_description():
    bag = True
    camera_share_dir = get_package_share_directory('chironix_camera')
    left_camera_calibration_file = join(camera_share_dir, 'calibrations', 'left.yaml')
    left_camera_calibration_uri = f'file://{left_camera_calibration_file}'
    right_camera_calibration_file = join(camera_share_dir, 'calibrations', 'right.yaml')
    right_camera_calibration_uri = f'file://{right_camera_calibration_file}'

    # BAG FILE
    bag_node = ExecuteProcess(
        cmd=[
            "ros2",
            "bag",
            "play",
            "--loop",
            "/workspace/bags/camera_bag/camera_bag.db3",
        ],
    )

    # LEFT NAMESPACE
    # LEFT DRIVER
    left_camera_node = Node(
        namespace='usb_cam_left',
        package='usb_cam',
        executable='usb_cam_node_exe',
        name='driver_node',
        parameters=[
            {'camera_info_url': left_camera_calibration_uri},
            {'pixel_format': 'mjpeg2rgb'},
            {'video_device': '/dev/video0'},
            {'camera_name': 'camera_left'},
            {'frame_id': 'camera_left_frame'},
        ],
    )

    # LEFT RECTIFIER
    left_rectifier_node = Node(
        namespace='usb_cam_left',
        package='image_proc',
        executable='rectify_node',
        name='rectify_node',
        remappings=[
            ('/usb_cam_left/image', '/usb_cam_left/image_raw'),
        ],
    )

    # RIGHT NAMESPACE
    # RIGHT DRIVER
    right_camera_node = Node(
        namespace='usb_cam_right',
        package='usb_cam',
        executable='usb_cam_node_exe',
        name='driver_node',
        parameters=[
            {'camera_info_url': right_camera_calibration_uri},
            {'pixel_format': 'mjpeg2rgb'},
            {'video_device': '/dev/video2'},
            {'camera_name': 'camera_right'},
            {'frame_id': 'camera_right_frame'},
        ],
    )

    # RIGHT RECTIFIER
    right_rectifier_node = Node(
        namespace='usb_cam_right',
        package='image_proc',
        executable='rectify_node',
        name='rectify_node',
        remappings=[
            ('/usb_cam_right/image', '/usb_cam_right/image_raw'),
        ],
    )

    # TRANSFORMS
    transform_node = Node(package = "tf2_ros",
        executable = "static_transform_publisher",
        arguments = ['-0.018649697552892808', '0.06954162974489837', '0.005019601880905415', '0.53378227645394', '0.03074957584054921', '-0.01565475977833588', 'camera_left_frame', 'camera_right_frame']
    )

    # STITCHER
    stitcher_node = Node(package = "chironix_camera",
        executable = "multi_camera_stitcher",
        name='stitcher_node',
    )

    real_nodes = [
        left_camera_node,
        left_rectifier_node,
        right_camera_node,
        right_rectifier_node
    ]
    bag_nodes = [bag_node]

    return LaunchDescription([
        *[node for node in real_nodes if not bag],
        *[node for node in bag_nodes if bag],
        transform_node,
        stitcher_node,
    ])