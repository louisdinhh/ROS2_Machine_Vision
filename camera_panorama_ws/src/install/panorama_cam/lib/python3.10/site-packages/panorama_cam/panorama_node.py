import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

class PanoramaNode(Node):
    def __init__(self):
        super().__init__('panorama_node')
        self.bridge = CvBridge()

        # ROS 2 Subscriptions for multiple cameras
        self.sub_camera1 = self.create_subscription(
            Image, '/camera1/image_raw', self.camera1_callback, 10)
        self.sub_camera2 = self.create_subscription(
            Image, '/camera2/image_raw', self.camera2_callback, 10)

        # Store frames
        self.frame1 = None
        self.frame2 = None

        # Initialize OpenGL
        self.width, self.height = 640, 480
        self.init_opengl()
        glutTimerFunc(16, self.update, 0)

    def init_opengl(self):
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(self.width * 2, self.height)
        glutCreateWindow("Panorama Camera Viewer")
        glutDisplayFunc(self.display)
        glEnable(GL_TEXTURE_2D)
        glClearColor(0.0, 0.0, 0.0, 1.0)

    def create_textures(self, frames):
        textures = glGenTextures(len(frames))
        for i, frame in enumerate(frames):
            glBindTexture(GL_TEXTURE_2D, textures[i])
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            frame = cv2.flip(frame, 0)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, frame.shape[1], frame.shape[0], 0,
                         GL_BGR, GL_UNSIGNED_BYTE, frame)
        return textures

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        if self.frame1 is not None and self.frame2 is not None:
            textures = self.create_textures([self.frame1, self.frame2])
            for i, texture in enumerate(textures):
                glBindTexture(GL_TEXTURE_2D, texture)
                x_offset = i * 2.0 - 1.0
                glBegin(GL_QUADS)
                glTexCoord2f(0.0, 0.0); glVertex2f(x_offset, -1.0)
                glTexCoord2f(1.0, 0.0); glVertex2f(x_offset + 1.0, -1.0)
                glTexCoord2f(1.0, 1.0); glVertex2f(x_offset + 1.0, 1.0)
                glTexCoord2f(0.0, 1.0); glVertex2f(x_offset, 1.0)
                glEnd()
            glutSwapBuffers()

    def update(self, value):
        glutPostRedisplay()
        glutTimerFunc(16, self.update, 0)

    def camera1_callback(self, msg):
        self.frame1 = self.bridge.imgmsg_to_cv2(msg, "bgr8")

    def camera2_callback(self, msg):
        self.frame2 = self.bridge.imgmsg_to_cv2(msg, "bgr8")

def main(args=None):
    rclpy.init(args=args)
    node = PanoramaNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
