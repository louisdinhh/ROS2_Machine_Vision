import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/louisdinhh/camera_panorama_ws/src/panorama_cam/install/panorama_cam'
