from rclpy.node import Node
from rclpy import init, spin, shutdown, Parameter
from rclpy.wait_for_message import wait_for_message
from sensor_msgs.msg import Image
from std_srvs.srv import Trigger
from time import sleep
from rclpy.time import Time
from rclpy.duration import Duration
from message_filters import Subscriber, ApproximateTimeSynchronizer
from cv_bridge import CvBridge
from os.path import join
from os import makedirs
from cv2 import imwrite


class MultiCameraCalibrationNode(Node):
    def __init__(self):
        super().__init__('multicamera_capture_node')
        # PARAMS
        self.calibration_reps = 100
        self.calibration_image_delay = Duration(seconds=0.5)
        self.topics = [
            '/usb_cam_left/image_rect',
            '/usb_cam_right/image_rect',
        ]


        # DEPENDENCIES
        self.srv = self.create_service(Trigger, '~/capture', self.begin_calibration)
        self.bridge = CvBridge()

        # DATA
        self.subs = []
        self.calibration_msgs = []
        self.synchronized_sub = None
        self.previous_time = None


    def begin_calibration(self, request, response):
        for topic in self.topics:
            self.subs.append(
                Subscriber(
                    self,
                    Image,
                    topic,
                )
            )
        synchronizer = ApproximateTimeSynchronizer(self.subs, 10, 0.5)
        synchronizer.registerCallback(self.synchronized_callback)
        self.calibration_msgs = [[] for topic in self.topics]
        response.success = True
        response.message = f"Succesfully begun calibration."
        return response


    def synchronized_callback(self, *args):
        current_time = self._time_from_msg(args[0].header.stamp)
        if self.previous_time is not None and ((current_time - self.previous_time) < self.calibration_image_delay):
            return

        self.get_logger().info(f"Capturing calibration image set [{len(self.calibration_msgs[0])+1}/{self.calibration_reps}]")
        for index, msg in enumerate(args):
            self.calibration_msgs[index].append(msg)

        self.previous_time = current_time
        if len(self.calibration_msgs[0]) >= self.calibration_reps:
            self.stop_calibration()
            self.get_logger().info("Captured all calibration images")
            self.dump_images("/workspace/extrinsic_camera_data")


    def stop_calibration(self):
        for sub in self.subs:
            self.destroy_subscription(sub.sub)
        self.subs = []
        self.synchronized_sub = None
        self.previous_time = None


    def dump_images(self, output_directory):
        self.get_logger().info(f"Saving image to: {output_directory}")
        for index, image_list in enumerate(self.calibration_msgs):
            camera_name = image_list[0].header.frame_id
            camera_name = f"camera_{index+1:03}"
            camera_directory = join(output_directory, camera_name)
            makedirs(camera_directory, exist_ok=True)
            for index, image in enumerate(image_list):
                cv_image = self.bridge.imgmsg_to_cv2(image, "bgr8")
                imwrite(
                    join(camera_directory, f"{index:05}.png"),
                    cv_image
                )


    def _time_from_msg(self, msg):
        return Time(seconds=msg.sec, nanoseconds=msg.nanosec)


# MAIN
def main(args=None):
    init(args=args)
    node = MultiCameraCalibrationNode()

    spin(node)

    node.destroy_node()
    shutdown()


if __name__ == '__main__':
    main()