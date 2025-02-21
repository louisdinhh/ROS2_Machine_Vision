import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import numpy as np
import cv2


class SurroundCam(Node):
    def __init__(self):
        super().__init__('surround_cam')

        # Subscribers for the cameras
        self.sub_camera1 = self.create_subscription(
            Image, '/camera1/image_rect', self.camera1_callback, 10)
        self.sub_camera2 = self.create_subscription(
            Image, '/camera2/image_rect', self.camera2_callback, 10)
        self.sub_camera3 = self.create_subscription(
            Image, '/camera3/image_rect', self.camera3_callback, 10)
        self.sub_camera4 = self.create_subscription(
            Image, '/camera4/image_rect', self.camera4_callback, 10)

        # Publisher for the stitched panoramic image
        self.pub_stitched_image = self.create_publisher(Image, '/output/panoramic_image', 10)

        # Bridge for ROS <-> OpenCV conversion
        self.bridge = CvBridge()

        # Placeholder images
        self.image1 = None
        self.image2 = None
        self.image3 = None
        self.image4 = None

    def camera1_callback(self, msg):
        """Callback for Camera 1"""
        self.image1 = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        self.stitch_images()

    def camera2_callback(self, msg):
        """Callback for Camera 2"""
        self.image2 = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        self.stitch_images()

    def camera3_callback(self, msg):
        """Callback for Camera 3"""
        self.image3 = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        self.stitch_images()

    def camera4_callback(self, msg):
        """Callback for Camera 4"""
        self.image4 = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        self.stitch_images()

    def stitch_images(self):
        """Blend images from all four cameras."""
        if self.image1 is not None and self.image2 is not None and self.image3 is not None and self.image4 is not None:
            try:
                # Blend the images using CPU processing
                blended_image = self.blend_images(self.image1, self.image2, self.image3, self.image4)

                # Publish the blended image
                stitched_msg = self.bridge.cv2_to_imgmsg(blended_image, encoding='bgr8')
                self.pub_stitched_image.publish(stitched_msg)

            except Exception as e:
                self.get_logger().error(f"Error during stitching: {e}")

    def blend_images(self, image1, image2, image3, image4):
        try:
            height = min(image1.shape[0], image2.shape[0], image3.shape[0], image4.shape[0])
            image1 = cv2.resize(image1, (image1.shape[1], height))
            image2 = cv2.resize(image2, (image2.shape[1], height))
            image3 = cv2.resize(image3, (image3.shape[1], height))
            image4 = cv2.resize(image4, (image4.shape[1], height))

            overlap_width = 140  

            # Calculate the total width of the stitched image
            blended_width = (
                image1.shape[1] + image2.shape[1] + image3.shape[1] + image4.shape[1] - 3 * overlap_width
            )

            blended_image = np.zeros((height, blended_width, 3), dtype=np.uint8)

            # Stitch first two images
            for x in range(overlap_width):
                alpha = x / overlap_width
                blended_image[:, image1.shape[1] - overlap_width + x] = (
                    (1 - alpha) * image1[:, image1.shape[1] - overlap_width + x] +
                    alpha * image2[:, x]
                ).astype(np.uint8)

            # Copy left and right sides for the first two images
            blended_image[:, :image1.shape[1] - overlap_width] = image1[:, :image1.shape[1] - overlap_width]
            blended_image[:, image1.shape[1]:image1.shape[1] + image2.shape[1] - overlap_width] = image2[:, overlap_width:]

            # Stitch the third image
            for x in range(overlap_width):
                alpha = x / overlap_width
                blended_image[:, image1.shape[1] + image2.shape[1] - 2 * overlap_width + x] = (
                    (1 - alpha) * image2[:, image2.shape[1] - overlap_width + x] +
                    alpha * image3[:, x]
                ).astype(np.uint8)

            # Copy left and right sides for the third image
            blended_image[:, image1.shape[1] + image2.shape[1] - overlap_width:
                        image1.shape[1] + image2.shape[1] + image3.shape[1] - 2 * overlap_width] = image3[:, overlap_width:]

            # Stitch the fourth image
            for x in range(overlap_width):
                alpha = x / overlap_width
                blended_image[:, image1.shape[1] + image2.shape[1] + image3.shape[1] - 3 * overlap_width + x] = (
                    (1 - alpha) * image3[:, image3.shape[1] - overlap_width + x] +
                    alpha * image4[:, x]
                ).astype(np.uint8)

            # Copy right side for the fourth image
            blended_image[:, image1.shape[1] + image2.shape[1] + image3.shape[1] - 2 * overlap_width:] = image4[:, overlap_width:]

            return blended_image
        except Exception as e:
            print(f"Error blending images: {e}")
            return None




def main(args=None):
    rclpy.init(args=args)
    node = SurroundCam()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
