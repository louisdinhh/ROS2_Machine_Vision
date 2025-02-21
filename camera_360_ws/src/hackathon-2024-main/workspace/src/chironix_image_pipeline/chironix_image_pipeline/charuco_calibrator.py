from __future__ import annotations
from typing import Tuple
import cv2
import numpy as np
from numpy import ndarray


class CharucoCalibrator:
    def __init__(self):
        self.board: cv2.aruco_CharucoBoard = None
        self.expected_num_corners: int = None
        self.out_shape: Tuple[float, float] = None
        self.target_points: ndarray = None
        self.camera_matrix = None
        self.dist_coeffs = None

        # aruco stuff
        self.index_1: int = None
        self.index_2: int = None
        self.index_3: int = None
        self.index_4: int = None

    def set_camera_matrix(self, cam_mat: ndarray):
        self.camera_matrix = cam_mat

    def set_dist_coeff(self, dist_coeffs: ndarray):
        self.dist_coeffs = dist_coeffs

    def _set_board(self, board: cv2.aruco_CharucoBoard):
        self.board = board
        all_col, all_row = self.board.getChessboardSize()
        col, row = (all_col - 1), (all_row - 1)  # board mode: only inside corner counts
        self.expected_num_corners = col * row

        # board corner index is bottom-top while we are expecting top-bot
        self.index_1 = (self.expected_num_corners - 1) - (col - 1)
        self.index_2 = self.expected_num_corners - 1
        self.index_3 = 0
        self.index_4 = col - 1

    def process_image(self, cv_image: ndarray) -> Tuple[ndarray, ndarray, ndarray]:
        """Return the homography, board_corners, board_corners_id"""
        h_matrix, charuco_corners, charuco_ids = None, None, None
        if self.camera_matrix is None or self.dist_coeffs is None:
            return h_matrix, charuco_corners, charuco_ids

        # Detect and guard if any aruco markers is there
        corners, ids, rejected = cv2.aruco.detectMarkers(cv_image, self.board.dictionary)
        if not corners:
            return h_matrix, charuco_corners, charuco_ids

        # Detect and refine board corners
        num_corner, charuco_corners, charuco_ids = cv2.aruco.interpolateCornersCharuco(
            corners,
            ids,
            cv_image,
            self.board,
            cameraMatrix=self.camera_matrix,
            distCoeffs=self.dist_coeffs,
        )
        self.board.getChessboardSize

        # guard if the corner is all there
        if num_corner < self.expected_num_corners:
            return h_matrix, charuco_corners, charuco_ids

        # define source point
        charuco_corners_2d = charuco_corners.reshape(-1, 2)  # 24 row, 2 column
        source_points = np.array(
            [
                charuco_corners_2d[self.index_1],
                charuco_corners_2d[self.index_2],
                charuco_corners_2d[self.index_3],
                charuco_corners_2d[self.index_4],
            ]
        )

        h_matrix, mask = cv2.findHomography(source_points, self.target_points)
        return h_matrix, charuco_corners, charuco_ids

    def draw_debug_image(self, img: ndarray, corners: ndarray, corner_ids: ndarray) -> ndarray:
        new_img = img.copy()
        corners_2di = np.int32(corners.reshape(-1, 2))  # convert to int, 2 column

        # draw corners id
        for corner, corner_id in zip(corners_2di, corner_ids):
            cv2.putText(
                new_img,
                str(corner_id),
                tuple(corner),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (180, 180, 180),
                2,
                cv2.LINE_AA,
            )

        # draw corner used to find transform
        cv2.circle(new_img, tuple(corners_2di[self.index_1]), 7, (120, 120, 120), -1)
        cv2.circle(new_img, tuple(corners_2di[self.index_2]), 7, (255, 0, 0), -1)
        cv2.circle(new_img, tuple(corners_2di[self.index_3]), 7, (0, 255, 0), -1)
        cv2.circle(new_img, tuple(corners_2di[self.index_4]), 7, (0, 0, 255), -1)

        return new_img

    def draw_warp_image(self, cv_image: ndarray, h_matrix: ndarray) -> ndarray:
        warped_img = cv2.warpPerspective(cv_image, h_matrix, self.out_shape)
        return warped_img

    def draw_board_image(self) -> ndarray:
        board_img = self.board.draw(self.out_shape)
        return board_img

    class Builder:
        def __init__(self):
            self.calibrator = CharucoCalibrator()
            self.ppm: float = None
            self.facing_deg = None
            self.facing_forward_m = None
            self.facing_left_m = None

        def configure_board(
            self, charuco_board: cv2.aruco_CharucoBoard
        ) -> CharucoCalibrator.Builder:
            """define what kind of board being used"""
            self.calibrator._set_board(charuco_board)
            return self

        def configure_output_img(
            self, width: int, height: int, pix_per_m: float
        ) -> CharucoCalibrator.Builder:
            """final output image size, how many pixel does one meter represent"""
            self.calibrator.out_shape = (width, height)
            self.ppm = pix_per_m
            return self

        def configure_facing(self, deg, forward_m, left_m) -> CharucoCalibrator.Builder:
            """where is the robot camera is facing, how far away the first corner of the board"""
            self.facing_deg = deg
            self.facing_forward_m = forward_m
            self.facing_left_m = left_m
            return self

        def build(self) -> CharucoCalibrator:
            img_centre_x = (self.calibrator.out_shape[0] / self.ppm) / 2
            img_centre_y = (self.calibrator.out_shape[1] / self.ppm) / 2
            x_pad = img_centre_x - self.facing_left_m
            y_pad = img_centre_y - self.facing_forward_m

            board_size = self.calibrator.board.getChessboardSize()
            num_square_x, num_square_y = (board_size[0] - 2, board_size[1] - 2)
            square_length = self.calibrator.board.getSquareLength()

            # square starting from top-left, top-right, bot-left, bot-right
            target_points = np.array(
                [
                    [x_pad, y_pad],
                    [x_pad + (num_square_x * square_length), y_pad],
                    [x_pad, y_pad + (num_square_y) * square_length],
                    [
                        x_pad + (num_square_x * square_length),
                        y_pad + (num_square_y) * square_length,
                    ],
                ]
            )
            target_points = self._rotate_at(
                target_points, self.facing_deg, (img_centre_x, img_centre_y)
            )
            target_points = target_points * self.ppm

            self.calibrator.target_points = target_points
            return self.calibrator

        def _rotate_at(self, points: ndarray, deg: float, centre: Tuple[int, int]) -> ndarray:
            angle_rad = np.radians(deg)
            translation = np.array([centre[0], centre[1]])
            rotation = np.array(
                [[np.cos(angle_rad), -np.sin(angle_rad)], [np.sin(angle_rad), np.cos(angle_rad)]]
            ).transpose()

            p_translated = points - translation
            rotated = p_translated @ rotation
            p_final = rotated + translation
            return p_final


class CharucoBoardBuilder:
    def __init__(self):
        self.dictionary = None
        self.column = None
        self.row = None
        self.square_len = None
        self.marker_len = None

    def configure_dictionary(self, dict_int: int) -> CharucoBoardBuilder:
        self.dictionary = cv2.aruco.Dictionary_get(dict_int)
        return self

    def configure_columns(self, square_x: int) -> CharucoBoardBuilder:
        self.column = square_x
        return self

    def configure_rows(self, square_y: int) -> CharucoBoardBuilder:
        self.row = square_y
        return self

    def configure_square_length(self, square_len: float) -> CharucoBoardBuilder:
        self.square_len = square_len
        return self

    def configure_marker_length(self, marker_len: float) -> CharucoBoardBuilder:
        self.marker_len = marker_len
        return self

    def build(self) -> cv2.aruco_CharucoBoard:
        aruco = cv2.aruco.CharucoBoard_create(
            self.column, self.row, self.square_len, self.marker_len, self.dictionary
        )
        return aruco
