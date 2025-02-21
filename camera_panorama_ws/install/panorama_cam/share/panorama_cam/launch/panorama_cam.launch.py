from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([

         # Left_Camera Node
        Node(
            package='v4l2_camera',
            executable='v4l2_camera_node',
            name='camera1',
            parameters=[
                {'video_device': '/dev/video0'},
            ],
            remappings=[
                ('/image_raw', '/camera1/image_raw'),
                ('/camera_info', '/camera1/camera_info')
            ],
        ),

        # Right_Camera Node
        Node(
            package='v4l2_camera',
            executable='v4l2_camera_node',
            name='camera2',
            parameters=[
                {'video_device': '/dev/video2'},  
            ],
            remappings=[
                ('/image_raw', '/camera2/image_raw'),
                ('/camera_info', '/camera2/camera_info')
            ],
        ),
        
        # Image_stitcher
         Node(
            package='panorama_cam',
            executable='panorama_node',
            name='panorama_node',
            output='screen'
        ),

        # Image View Node
        Node(
            package='rqt_image_view',
            executable='rqt_image_view',
            name='rqt_image_view',
        )
    ])