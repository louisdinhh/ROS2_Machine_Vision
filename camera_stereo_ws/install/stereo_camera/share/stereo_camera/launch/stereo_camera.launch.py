from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Left_Camera Node
        Node(
            package='v4l2_camera',
            executable='v4l2_camera_node',
            name='camera_node',
            parameters=[
                {'video_device': '/dev/video0'},  # Replace with the correct video device
               {'camera_info_url': 'file:///home/louisdinhh/.ros/camera_info/left.yaml'}
            ],
            remappings=[
                ('/image_raw', '/stereo/left/image_raw'),
                ('/camera_info', '/stereo/left/camera_info')
            ],
        ),

        # Right_Camera Node
        Node(
            package='v4l2_camera',
            executable='v4l2_camera_node',
            name='camera_node',
            parameters=[
                {'video_device': '/dev/video2'},  # Replace with the correct video device
                {'camera_info_url': 'file:///home/louisdinhh/.ros/camera_info/right.yaml'}
            ],
            remappings=[
                ('/image_raw', '/stereo/right/image_raw'),
                ('/camera_info', '/stereo/right/camera_info')
            ],
        ),

        # Image Processing Node LEFT
        Node(
            package='image_proc',
            executable='image_proc',
            name='image_proc_node_1',
            remappings=[
                ('/image', '/stereo/left/image_raw'),
                ('/camera_info', '/stereo/left/camera_info'),
                ('/image_rect', '/stereo/left/image_rect'),
            ]
        ),

        # Image Processing Node RIGHT
        Node(
            package='image_proc',
            executable='image_proc',
            name='image_proc_node_2',
            remappings=[
                ('/image', '/stereo/right/image_raw'),
                ('/camera_info', '/stereo/right/camera_info'),
                ('/image_rect', '/stereo/right/image_rect'),
            ]
        ),

        # Image View Node
        Node(
            package='rqt_image_view',
            executable='rqt_image_view',
            name='rqt_image_view',
        )
    ])
