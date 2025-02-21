import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import numpy as np
import cv2
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

class PanoramaNode(Node):
    def __init__(self):
        super().__init__('panorama_node')
        
        # Initialize the ROS publisher for the panorama image
        self.publisher = self.create_publisher(Image, '/panorama_image', 10)

        # Initialize CvBridge to convert OpenCV images to ROS messages
        self.bridge = CvBridge()

        # Set up a timer to periodically publish the panorama image
        self.timer = self.create_timer(0.1, self.publish_panorama_callback)

        # Initialize OpenGL context (you may need to customize this based on your OpenGL setup)
        self.init_opengl()

        # Camera frames
        self.frame1 = None
        self.frame2 = None

        # Subscribe to V4L2 camera topics (replace with actual topics)
        self.create_subscription(Image, '/camera1/image_raw', self.camera1_callback, 10)
        self.create_subscription(Image, '/camera2/image_raw', self.camera2_callback, 10)

    def init_opengl(self):
        # Initialize OpenGL context for rendering
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
        glutCreateWindow("Panorama Rendering")
        
        # OpenGL setup (e.g., projection, modelview, etc.)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)

        # Any other OpenGL setup related to rendering your panorama

    def render_panorama(self):
        # OpenGL rendering code to generate the panorama
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Render your panorama using OpenGL commands
        # e.g., draw your 3D scene, apply textures, projections, etc.
        
        # After rendering, capture the framebuffer content
        width, height = 800, 600  # Replace with your framebuffer dimensions
        pixels = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)

        # Convert the raw pixel data into an OpenCV image (numpy array)
        panorama_image = np.frombuffer(pixels, dtype=np.uint8).reshape(height, width, 3)
        panorama_image = cv2.flip(panorama_image, 0)  # Flip if needed (OpenGL and OpenCV may differ in origin)
        
        return panorama_image

    def publish_panorama(self, panorama_image):
        try:
            # Convert the OpenCV panorama image to a ROS Image message
            ros_image = self.bridge.cv2_to_imgmsg(panorama_image, encoding="bgr8")

            # Publish the panorama image
            self.publisher.publish(ros_image)
            self.get_logger().info("Panorama image published")
        except Exception as e:
            self.get_logger().error(f"Failed to publish panorama image: {e}")

    def publish_panorama_callback(self):
        # Generate or render the panorama image using OpenGL
        if self.frame1 is not None and self.frame2 is not None:
            panorama_image = self.render_panorama()
            self.publish_panorama(panorama_image)

    def camera1_callback(self, msg):
        # Process camera 1 frame (store it in self.frame1)
        self.frame1 = self.bridge.imgmsg_to_cv2(msg, "bgr8")

    def camera2_callback(self, msg):
        # Process camera 2 frame (store it in self.frame2)
        self.frame2 = self.bridge.imgmsg_to_cv2(msg, "bgr8")

def main(args=None):
    rclpy.init(args=args)
    node = PanoramaNode()

    # Spin the node to handle ROS 2 communications
    rclpy.spin(node)

    # Clean up before shutdown
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
