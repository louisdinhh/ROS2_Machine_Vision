#!/usr/bin/env python3

from __future__ import annotations
import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, CameraInfo
from chironix_image_pipeline.charuco_calibrator import CharucoCalibrator, CharucoBoardBuilder


class CharucoCalibratorNode(Node):
    def __init__(self):
        super().__init__("charuco_calibrator_node")
        self.get_logger().info("charuco_calibrator_node initialising...")
        self.declare_parameter("out_width", 1920)
        self.declare_parameter("out_height", 1200)
        self.declare_parameter("pixel_per_meter", 300)
        self.declare_parameter("facing_deg", 0)  # clockwise fw=0, right=90, back=180, left=270
        self.declare_parameter("facing_forward_m", 0.5)  # distance to corner zero
        self.declare_parameter("facing_left_m", 0.6)  # distance to corner zero, positive left

        out_width = self.get_parameter("out_width").value
        out_height = self.get_parameter("out_height").value
        pixpm = self.get_parameter("pixel_per_meter").value
        facing_deg = self.get_parameter("facing_deg").value
        dist_height = self.get_parameter("facing_forward_m").value
        dist_width = self.get_parameter("facing_left_m").value

        bd_board = (
            CharucoBoardBuilder()
            .configure_columns(9)
            .configure_rows(4)
            .configure_square_length(0.115)
            .configure_marker_length(0.09)
            .configure_dictionary(0)  # cv2.aruco.DICT_4X4_50
            .build()
        )

        self.calibrator: CharucoCalibrator = (
            CharucoCalibrator.Builder()
            .configure_board(bd_board)
            .configure_output_img(out_width, out_height, pixpm)
            .configure_facing(facing_deg, dist_height, dist_width)
            .build()
        )

        self.cvbridge = CvBridge()

        # sub/pub
        self.image_sub = self.create_subscription(Image, "/usb_cam/rect/image", self.image_cb, 1)
        self.cam_info_sub = self.create_subscription(
            CameraInfo, "/usb_cam/rect/camera_info", self.cam_info_cb, 1
        )
        self.debug_pub = self.create_publisher(Image, "/usb_cam/debug/debug_image", 1)
        self.output_pub = self.create_publisher(Image, "/usb_cam/debug/output_image", 1)
        self.board_pub = self.create_publisher(Image, "/usb_cam/debug/board_image", 1)

        self.get_logger().info("charuco_calibrator_node has been started.")

    def image_cb(self, img_msg: Image):
        cv_image = self.cvbridge.imgmsg_to_cv2(img_msg, desired_encoding="rgb8")
        h_matrix, corners, corners_id = self.calibrator.process_image(cv_image)

        self.get_logger().info(f"homography matrix: \n{h_matrix}", throttle_duration_sec=3.0)

        board_img = self.calibrator.draw_board_image()
        board_msg = self.cvbridge.cv2_to_imgmsg(board_img, "mono8", img_msg.header)
        self.board_pub.publish(board_msg)

        if corners is not None and corners_id is not None:
            debug_img = self.calibrator.draw_debug_image(cv_image, corners, corners_id)
            debug_msg = self.cvbridge.cv2_to_imgmsg(debug_img, "rgb8", img_msg.header)
            self.debug_pub.publish(debug_msg)

        if h_matrix is not None:
            warp_img = self.calibrator.draw_warp_image(cv_image, h_matrix)
            warp_msg = self.cvbridge.cv2_to_imgmsg(warp_img, "rgb8", img_msg.header)
            self.output_pub.publish(warp_msg)

    def cam_info_cb(self, cam_info_msg: CameraInfo):
        cam_matrix = np.array(cam_info_msg.k).reshape(3, 3)
        self.calibrator.set_camera_matrix(cam_matrix)

        dist_coeff = np.array(cam_info_msg.d)
        self.calibrator.set_dist_coeff(dist_coeff)

        self.destroy_subscription(self.cam_info_sub)

    def destroy_node(self):
        self.get_logger().info("charuco_calibrator_node shutting down...")
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    ccnode = CharucoCalibratorNode()
    try:
        rclpy.spin(ccnode)
    except KeyboardInterrupt:
        pass
    finally:
        ccnode.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
