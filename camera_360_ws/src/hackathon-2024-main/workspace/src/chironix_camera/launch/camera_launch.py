from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from os.path import join

def generate_launch_description():
    # LEFT NAMESPACE
    # LEFT DRIVER
    left_camera_node = Node(
        namespace='usb_cam_left',
        package='usb_cam',
        executable='usb_cam_node_exe',
        name='driver_node',
        parameters=[
            {'pixel_format': 'mjpeg2rgb'},
            {'video_device': '/dev/video0'},
            {'camera_name': 'camera_left'},
            {'camera_frame_id': 'camera_left_frame'},
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
            {'pixel_format': 'mjpeg2rgb'},
            {'video_device': '/dev/video2'},
            {'camera_name': 'camera_right'},
            {'camera_frame_id': 'camera_right_frame'},
        ],
    )

    return LaunchDescription([
        left_camera_node,
        right_camera_node,
    ])