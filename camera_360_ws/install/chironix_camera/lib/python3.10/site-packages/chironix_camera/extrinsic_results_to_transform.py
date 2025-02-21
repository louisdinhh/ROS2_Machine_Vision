from cv2 import FileStorage, FILE_STORAGE_READ
from tf_transformations import (
    euler_from_matrix,
    translation_from_matrix,
    euler_matrix,
    inverse_matrix
)
from math import pi
from numpy import dot, linalg

def main():
    results_file = "/workspace/extrinsic_camera_data/results/calibrated_cameras_data.yml"
    fs = FileStorage(results_file, FILE_STORAGE_READ)

    tf_matrix = fs.getNode("camera_1").getNode("camera_pose_matrix").mat()
    camera_to_ros_tf = euler_matrix(pi/2,-pi/2,0)
    ros_to_camera_tf = linalg.inv(camera_to_ros_tf)

    corrected_matrix =  camera_to_ros_tf @ tf_matrix @ ros_to_camera_tf

    translation = list(translation_from_matrix(ros_to_camera_tf @ tf_matrix))
    euler = list(euler_from_matrix(corrected_matrix))
    transform_nums = [str(num) for num in (translation+euler+["camera_left_frame", "camera_right_frame"])]
    print("--------------- TRANSFORM ---------------")
    print(transform_nums)

if __name__ == "__main__":
    main()