from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Camera 1 Node
        Node(
            package='v4l2_camera',
            executable='v4l2_camera_node',
            name='camera1_node',
            parameters=[
            	{'frame_rate': 31.0},  # Set the desired frame rate
                {'video_device': '/dev/video2'},  # Device for Camera 1
                {'image_size': [640, 480]},
                #{'image_format': 'mjpeg'},  # Request MJPEG format
                {'camera_name': 'camera1_calibration'},  # Calibration name for Camera 1
                {'camera_info_url': 'file:///home/louisdinhh/camera_360_ws/src/panorama_cam/camera_info/camera1.yaml'}  # Calibration file for Camera 1
            ],
            remappings=[
                ('/image_raw', '/camera1/image_raw'),
                ('/camera_info', '/camera1/camera_info')
            ],
        ),
        # Rectification Node for Camera 1
        Node(
            package='image_proc',
            executable='image_proc',
            name='camera1_rectifier',
            parameters=[{'approximate_sync': True, 'slop': 0.25, 'queue_size': 10,}],  # Add approximate_sync and slop
            remappings=[
                ('/image', '/camera1/image_raw'),
                ('/camera_info', '/camera1/camera_info'),
                ('/image_rect', '/camera1/image_rect')
            ],
        ),
        # Camera 2 Node
        Node(
            package='v4l2_camera',
            executable='v4l2_camera_node',
            name='camera2_node',
            parameters=[
            	{'frame_rate': 31.0},  # Set the desired frame rate
                {'video_device': '/dev/video4'},  # Device for Camera 2
                {'image_size': [640, 480]},
                #{'image_format': 'mjpeg'},  # Request MJPEG format
                {'camera_name': 'camera2_calibration'},  # Calibration name for Camera 2
                {'camera_info_url': 'file:///home/louisdinhh/camera_360_ws/src/panorama_cam/camera_info/camera2.yaml'}  # Calibration file for Camera 2
            ],
            remappings=[
                ('/image_raw', '/camera2/image_raw'),
                ('/camera_info', '/camera2/camera_info')
            ],
        ),
        # Rectification Node for Camera 2
        Node(
            package='image_proc',
            executable='image_proc',
            name='camera2_rectifier',
            parameters=[{'approximate_sync': True, 'slop': 0.25, 'queue_size': 10,}],  # Add approximate_sync and slop
            remappings=[
                ('/image', '/camera2/image_raw'),
                ('/camera_info', '/camera2/camera_info'),
                ('/image_rect', '/camera2/image_rect')
            ],
        ),
    ])