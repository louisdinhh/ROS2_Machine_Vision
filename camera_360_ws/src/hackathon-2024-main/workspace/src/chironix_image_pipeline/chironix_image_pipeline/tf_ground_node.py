#!/usr/bin/env python3

# WIP
# The idea is to calculate the homography matrix from tf.

import rclpy
from rclpy.node import Node
import rclpy.time
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import PointStamped, TransformStamped
from cv_bridge import CvBridge
import cv2
import numpy as np
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from tf2_ros import TransformException
from rclpy.time import Time, Duration
import numpy as np
import tf_transformations
import time

from scipy.spatial.transform import Rotation

class ImageSubscriberPublisher(Node):
    def __init__(self):
        super().__init__("image_subscriber_publisher")
        self.buffer = Buffer()
        self.tf_listener = TransformListener(self.buffer, self)
        self.tf_max_wait = 1.0

        self.cam_info = None
        self.source_frame = "usb_cam_optical"
        self.target_frame = "reproject_cam_optical"
        self.reproj_matrix = None

        self.image_sub = self.create_subscription(Image, "/usb_cam/rect/image", self.image_cb, 1)
        self.camera_info_sub = self.create_subscription(
            CameraInfo, "/usb_cam/rect/camera_info", self.camera_info_cb, 1
        )
        self.publisher = self.create_publisher(Image, "/usb_cam/reproj/image", 1)
        self.camera_info_pub = self.create_publisher(CameraInfo, "/usb_cam/reproj/camera_info", 1)

        self.bridge = CvBridge()
        self.get_logger().info("Image subscriber and publisher node has been started.")

    def image_cb(self, msg: Image):
        if self.reproj_matrix is None:
            self.get_logger().info("Still waiting reproj matrix", once=True)
            self.calc_reproj_matrix()
            return

        # Convert ROS Image message to OpenCV image
        cv_image: np.ndarray = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        # Process the image (in this example, we'll just convert it to grayscale)

        # gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        # output_msg = self.bridge.cv2_to_imgmsg(gray_image, encoding="mono8")

        reproj_image = cv2.warpPerspective(
            cv_image, self.homography_matrix, (cv_image.shape[1], cv_image.shape[2])
        )
        output_msg = self.bridge.cv2_to_imgmsg(reproj_image, encoding="rgb8")
        output_msg.header = msg.header
        output_msg.header.frame_id = self.target_frame
        # Publish the processed image
        self.publisher.publish(output_msg)
        self.get_logger().info("Processed image has been published.", once=True)

    def camera_info_cb(self, msg: CameraInfo):
        if self.reproj_matrix is None:
            self.get_logger().info("Cam info waiting reproj matrix", once=True)
            return
        new_camera_info = CameraInfo()
        new_camera_info.header = msg.header
        new_camera_info.height = msg.height
        new_camera_info.width = msg.width

        original_K = np.array(msg.k).reshape(3, 3)
        new_K = self.reproj_matrix @ original_K
        new_camera_info.k = new_K.flatten().tolist()

        original_P = np.array(msg.p).reshape(3, 4)
        new_P = np.dot(self.reproj_matrix, original_P[:, :3])
        new_camera_info.p = new_P.flatten().tolist() + [
            original_P[0, 3],
            original_P[1, 3],
            original_P[2, 3],
        ]

        new_camera_info.d = list(msg.d)

        new_camera_info.r = list(msg.r)

        new_camera_info.header = msg.header
        new_camera_info.header.frame_id = self.target_frame
        self.camera_info_pub.publish(new_camera_info)

    def calc_reproj_matrix(self):
        found = False
        start_time = time.time()
        while not found and (time.time() - start_time < self.tf_max_wait):
            try:
                tf_stamped: TransformStamped = self.buffer.lookup_transform(
                    self.source_frame, self.target_frame, Time()
                )
                found = True
                self.get_logger().info("Transform found!")
            except TransformException as te:
                self.get_logger().info("Transform not found retrying...")
                time.sleep(0.1)

        if not found:
            return

        print(tf_stamped)
        # reproj_to_usb
        tx = tf_stamped.transform.translation.x
        ty = tf_stamped.transform.translation.y
        tz = tf_stamped.transform.translation.z
        qx = tf_stamped.transform.rotation.x
        qy = tf_stamped.transform.rotation.y
        qz = tf_stamped.transform.rotation.z
        qw = tf_stamped.transform.rotation.w

        rot_tf = tf_transformations.quaternion_matrix([qx, qy, qz, qw])
        print(f"rotation tf: {rot_tf}")

        self.reproj_matrix = np.array(
            [[rot_tf[0][0], rot_tf[0][1], tx], [rot_tf[1][0], rot_tf[1][1], ty], [0, 0, 1]]
        )
        rotation_matrix = rot_tf[:3, :3]
        print(f"rotation_matrix: {rotation_matrix}")
        print(Rotation.from_matrix(rotation_matrix).as_euler("xyz", degrees=True))

        self.homography_matrix = np.array([
            [rotation_matrix[0][0], rotation_matrix[0][1], tx],
            [rotation_matrix[1][0], rotation_matrix[1][1], ty],
            [rotation_matrix[2][0], rotation_matrix[2][1], 1.0]  # Add perspective component
        ])
        print("------") 
        print(self.homography_matrix)


def main(args=None):
    rclpy.init(args=args)
    node = ImageSubscriberPublisher()
    node.get_clock
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
