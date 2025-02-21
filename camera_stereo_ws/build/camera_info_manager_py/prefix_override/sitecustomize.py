import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/louisdinhh/camera_stereo_ws/install/camera_info_manager_py'
