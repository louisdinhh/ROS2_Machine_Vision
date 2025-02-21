from camera_calibration.calibrator import MonoCalibrator, Patterns, ChessboardInfo
import cv2
from os.path import join

def main():
    image_dir = "/workspace/calibration/camera_001"
    image_paths = (join(image_dir, f"{count:05}.png") for count in range(0,100))
    boards = [
        ChessboardInfo(
            'charuco', n_cols=7, n_rows=3, dim=0.115, marker_size=0.09,aruco_dict="4x4_50"
        )
    ]

    # Steal their flag stuff
    num_ks = 2
    fix_principal_point = False
    fix_aspect_ratio = False
    zero_tangent_dist = False

    calib_flags = 0
    if fix_principal_point:
        calib_flags |= cv2.CALIB_FIX_PRINCIPAL_POINT
    if fix_aspect_ratio:
        calib_flags |= cv2.CALIB_FIX_ASPECT_RATIO
    if zero_tangent_dist:
        calib_flags |= cv2.CALIB_ZERO_TANGENT_DIST
    if (num_ks > 3):
        calib_flags |= cv2.CALIB_RATIONAL_MODEL
    if (num_ks < 6):
        calib_flags |= cv2.CALIB_FIX_K6
    if (num_ks < 5):
        calib_flags |= cv2.CALIB_FIX_K5
    if (num_ks < 4):
        calib_flags |= cv2.CALIB_FIX_K4
    if (num_ks < 3):
        calib_flags |= cv2.CALIB_FIX_K3
    if (num_ks < 2):
        calib_flags |= cv2.CALIB_FIX_K2
    if (num_ks < 1):
        calib_flags |= cv2.CALIB_FIX_K1


    images = [cv2.imread(path) for path in image_paths]
    mc = MonoCalibrator(boards=boards, flags=calib_flags, pattern=Patterns.ChArUco)
    mc.cal(images)
    print(mc.yaml())

if __name__ == "__main__":
    main()