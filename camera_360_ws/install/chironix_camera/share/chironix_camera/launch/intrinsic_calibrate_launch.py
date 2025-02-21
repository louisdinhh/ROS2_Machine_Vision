from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # LEFT
        Node(
            namespace='usb_cam_left',
            package='camera_calibration',
            executable='cameracalibrator',
            name='camera_calibration_node',
            remappings=[
                ('/usb_cam_left/image', '/usb_cam_left/image_raw'),
            ],
            parameters=[
                {'camera': '/usb_cam_left'}
            ],
            arguments=[
                '--size', '8x3',
                '--square', '0.115',
                # '--charuco_marker_size', '0.09',
                # '--aruco_dict', '4x4_50',
                # '--pattern', 'charuco'
            ]
        ),
        # RIGHT
        # Node(
        #     namespace='usb_cam_right',
        #     package='camera_calibration',
        #     executable='cameracalibrator',
        #     name='camera_calibration_node',
        #     remappings=[
        #         ('~/image', '~/image_raw'),
        #     ],
        #     parameters=[
        #         {'camera': '/usb_cam_right'}
        #     ],
        #     arguments=[
        #         '--size', '8x3',
        #         '--square', '0.115',
        #         # '--charuco_marker_size', '0.09',
        #         # '--aruco_dict', '4x4_50',
        #         # '--pattern', 'charuco'
        #     ]
        # )
    ])