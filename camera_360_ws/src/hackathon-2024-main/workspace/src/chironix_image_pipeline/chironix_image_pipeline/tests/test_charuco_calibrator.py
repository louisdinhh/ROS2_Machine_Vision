import unittest
from chironix_image_pipeline.charuco_calibrator import CharucoCalibrator, CharucoBoardBuilder
import cv2
from pathlib import Path
import numpy as np


class TestCharucoCalibrator(unittest.TestCase):
    def setUp(self):
        self.cam_matrix = np.array(
            [
                [899.36352539, 0.0, 950.07330322],
                [0.0, 900.71374512, 584.32824707],
                [0.0, 0.0, 1.0],
            ]
        )
        self.dist_coeff = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        self.charuco_board = (
            CharucoBoardBuilder()
            .configure_columns(9)
            .configure_rows(4)
            .configure_square_length(0.115)
            .configure_marker_length(0.09)
            .configure_dictionary(0)  # cv2.aruco.DICT_4X4_50
            .build()
        )

        self.calibrator = (
            CharucoCalibrator.Builder()
            .configure_board(self.charuco_board)
            .configure_output_img(1920, 1200, 300)
            .configure_facing(0, 0.5, 0.6)
            .build()
        )

    def test_charuco_board_build__true(self):
        self.assertIsNotNone(self.charuco_board)

    def test_charuco_calibrator_build__true(self):
        self.assertIsNotNone(self.calibrator)

    def test_process_image__image__true(self):
        self.calibrator.set_camera_matrix(self.cam_matrix)
        self.calibrator.set_dist_coeff(self.dist_coeff)

        current_file = Path(__file__)
        img_file = current_file.parent.parent.parent / "bags" / "sample_image.jpg"
        cv_image = cv2.imread(str(img_file.absolute()))

        h, corners, corner_ids = self.calibrator.process_image(cv_image)

        self.assertTrue(corners.size > 0)
        board_img = self.calibrator.draw_board_image()  # noqa: F841
        debug_img = self.calibrator.draw_debug_image(cv_image, corners, corner_ids)  # noqa: F841
        warp_img = self.calibrator.draw_warp_image(cv_image, h)  # noqa: F841
        # cv2.imshow('Image', board_img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()


if __name__ == "__main__":
    unittest.main()
