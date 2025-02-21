import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/louisdinhh/camera_lidar_ws/install/ros2_camera_lidar_fusion'
