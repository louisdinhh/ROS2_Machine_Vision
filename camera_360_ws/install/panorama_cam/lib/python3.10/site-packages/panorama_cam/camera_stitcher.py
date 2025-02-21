import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import numpy as np
import cv2


class PanoramicImageMerger(Node):
    def __init__(self):
        super().__init__('panoramic_image_merger')

        # Subscribers for the two cameras
        self.sub_camera1 = self.create_subscription(
            Image, '/camera1/image_rect', self.camera1_callback, 10)
        self.sub_camera2 = self.create_subscription(
            Image, '/camera2/image_rect', self.camera2_callback, 10)

        # Publisher for the stitched panoramic image
        self.pub_stitched_image = self.create_publisher(Image, '/output/panoramic_image', 10)

        # Bridge for ROS <-> OpenCV conversion
        self.bridge = CvBridge()

        # Placeholder images
        self.image1 = None
        self.image2 = None

    def camera1_callback(self, msg):
        """Callback for Camera 1"""
        self.image1 = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        self.stitch_images()

    def camera2_callback(self, msg):
        """Callback for Camera 2"""
        self.image2 = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        self.stitch_images()

    def stitch_images(self):
        """Blend images from both cameras using CPU."""
        if self.image1 is not None and self.image2 is not None:
            try:
                # Blend the images using CPU processing
                blended_image = self.blend_images(self.image1, self.image2)

                # Publish the blended image
                stitched_msg = self.bridge.cv2_to_imgmsg(blended_image, encoding='bgr8')
                self.pub_stitched_image.publish(stitched_msg)

            except Exception as e:
                self.get_logger().error(f"Error during stitching: {e}")
                

    def blend_images(self, image1, image2):
        """Blend two images with simple overlap and fade."""
        try:
            # Resize images to the same height
            height = min(image1.shape[0], image2.shape[0])
            image1 = cv2.resize(image1, (image1.shape[1], height))
            image2 = cv2.resize(image2, (image2.shape[1], height))

            # Define overlap width
            overlap_width = 140  # Adjust based on your setup

            # Calculate the total width of the blended image
            blended_width = image1.shape[1] + image2.shape[1] - overlap_width

            # Create a blank image for the blended output
            blended_image = np.zeros((height, blended_width, 3), dtype=np.uint8)

            # Copy the left side of the first image
            blended_image[:, :image1.shape[1] - overlap_width] = image1[:, :image1.shape[1] - overlap_width]

            # Copy the right side of the second image
            blended_image[:, image1.shape[1]:] = image2[:, overlap_width:]

            # Blend the overlapping region with a linear fade
            for x in range(overlap_width):
                alpha = x / overlap_width  # Linear blend weight
                blended_image[:, image1.shape[1] - overlap_width + x] = (
                    (1 - alpha) * image1[:, image1.shape[1] - overlap_width + x] +
                    alpha * image2[:, x]
                ).astype(np.uint8)

            return blended_image

        except Exception as e:
            self.get_logger().error(f"Error during blending: {e}")
            return image1  # Fallback to the first image


def main(args=None):
    rclpy.init(args=args)
    node = PanoramicImageMerger()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
