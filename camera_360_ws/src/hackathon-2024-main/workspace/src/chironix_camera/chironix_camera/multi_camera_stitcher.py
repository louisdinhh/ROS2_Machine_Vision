from rclpy.node import Node
from rclpy import init, spin, shutdown, Parameter
from sensor_msgs.msg import Image
from message_filters import Subscriber, ApproximateTimeSynchronizer
from cv_bridge import CvBridge
from cv2 import hconcat, imshow, waitKey, ORB_create, BFMatcher, drawKeypoints, drawMatches, DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS, RANSAC, findHomography, perspectiveTransform, warpPerspective, cvtColor, COLOR_BGR2GRAY, \
    polylines, LINE_AA, addWeighted, KeyPoint, DMatch, copyMakeBorder, BORDER_CONSTANT
from numpy import float32, zeros, int32, abs, sum, mean, stack, any, percentile
from omniglue import OmniGlue

class MultiCamStitcher:
    HOMOGRAPHY_AVERAGE_WINDOW = 40
    HOMOGRAPHY_STABLE_DIFFERENCE = 20

    def __init__(self, logger, matched_publisher, overlapped_publisher, stitched_publisher, bridge, matcher):
        self.logger = logger
        self.matched_publisher = matched_publisher
        self.overlapped_publisher = overlapped_publisher
        self.stitched_publisher = stitched_publisher
        self.bridge = bridge
        self.matcher = matcher
        self.homography = zeros([3,3])
        self.homography_log = []

    def image_callback(self, img1_msg, img2_msg):
        img1 = self.bridge.imgmsg_to_cv2(img1_msg, "bgr8")
        img2 = self.bridge.imgmsg_to_cv2(img2_msg, "bgr8")

        if len(self.homography_log) <= MultiCamStitcher.HOMOGRAPHY_AVERAGE_WINDOW:
            pts1, pts2 = self.matcher.get_matches(img1, img2)
            self.homography = self.get_homography(pts1, pts2)
            matched_image = self.matched_image(img1, img2, pts1, pts2)
            if matched_image is not None:
                self.matched_publisher.publish(
                    self.bridge.cv2_to_imgmsg(matched_image, encoding="bgr8")
                )

        self.overlapped_publisher.publish(
            self.bridge.cv2_to_imgmsg(
                self.overlap_image(img1, img2, self.homography),
                encoding="bgr8"
            )
        )

        self.stitched_publisher.publish(
            self.bridge.cv2_to_imgmsg(
                self.stitch_image(img1, img2, self.homography),
                encoding="bgr8"
            )
        )

    def get_homography(self, pts1, pts2):
        if len(pts1) < 10:
            return self.homography

        np_pts1 = float32(pts1).reshape(-1,1,2)
        np_pts2 = float32(pts2).reshape(-1,1,2)
        homography, mask = findHomography(np_pts2, np_pts1, RANSAC, 5.0) # Transfer from img2 to img1 plane.
        if len(self.homography_log) > 10 and self.is_homography_outlier(homography):
            return self.homography

        self.homography_log.append(homography)
        return mean(stack(self.homography_log), axis=0)

    def is_homography_outlier(self, homography):
        q1 = percentile(self.homography_log, 20, axis=0)
        q3 = percentile(self.homography_log, 80, axis=0)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        return any((homography < lower_bound) | (homography > upper_bound))


    def matched_image(self, img1, img2, pts1, pts2):
        kp1 = [KeyPoint(*pt, 2) for pt in pts1]
        kp2 = [KeyPoint(*pt, 2) for pt in pts2]
        matches = [DMatch(index, index, 0) for index, pt in enumerate(pts1)]
        return drawMatches(img1,kp1,img2,kp2,matches,None,flags=DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

    def overlap_image(self, img1, img2, homography):
        img2_warped = warpPerspective(img2, self.homography,(img1.shape[1]+img2.shape[1], img1.shape[0]))
        img1_padded = copyMakeBorder(
            img1, 
            top=0, 
            bottom=0, 
            left=0, 
            right=img2.shape[1], 
            borderType=BORDER_CONSTANT, 
            value=[0, 0, 0]
        )
        return addWeighted(img1_padded, 0.5, img2_warped, 0.5, 0.0, None)

    def stitch_image(self, img1, img2, homography):
        img2_warped = warpPerspective(img2, self.homography,(img1.shape[1]+img2.shape[1], img1.shape[0]))
        img2_warped[0:img1.shape[0], 0:img1.shape[1]] = img1
        return img2_warped


class OmniGlueFeatureMatcher:
    GOOD_MATCH_CONFIDENCE = 0.3 # Must be greater than 80% confidence

    def __init__(self):
        self.glue = OmniGlue(
            og_export='/omniglue/models/og_export',
            sp_export='/omniglue/models/sp_v6',
            dino_export='/omniglue/models/dinov2_vitb14_pretrain.pth',
            )

    def get_matches(self, image1, image2):
        kp1, kp2, match_confidences = self.glue.FindMatches(image1, image2)
        kp1_good = []
        kp2_good = []
        for index, conf in enumerate(match_confidences):
            if conf > OmniGlueFeatureMatcher.GOOD_MATCH_CONFIDENCE:
                kp1_good.append(kp1[index])
                kp2_good.append(kp2[index])
        return (kp1_good, kp2_good)


class CV2FeatureMatcher:
    GOOD_MATCH_DISTANCE_RATIO = 0.7 # Must be 0.7x the distance to the next best match (or smaller)

    def __init__(self):
        self.feature_detector = ORB_create()
        self.feature_matcher = BFMatcher()

    def get_matches(self, image1, image2):
        img1_grey = cvtColor(image1, COLOR_BGR2GRAY)
        img2_grey = cvtColor(image2, COLOR_BGR2GRAY)
        kp1, des1 = self.feature_detector.detectAndCompute(img1_grey,None)
        kp2, des2 = self.feature_detector.detectAndCompute(img2_grey,None)
        matches = self.feature_matcher.knnMatch(des1,des2, k=2) # Query, Train, Find 2 matches per features
        good_matches = [
            match1 for (match1, match2) in matches if
            match1.distance < CV2FeatureMatcher.GOOD_MATCH_DISTANCE_RATIO*match2.distance
        ]
        return (
            [kp1[match.queryIdx].pt for match in good_matches],
            [kp2[match.trainIdx].pt for match in good_matches]
        )


class ROSNode(Node):
    def __init__(self):
        super().__init__('multicamera_stitcher_node')

        # PARAMS
        self.declare_parameters(
            namespace='',
            parameters=[
                ('stitch_topics', ['/usb_cam_right/image_rect', '/usb_cam_left/image_rect']),
                ('publish_topics', ['/usb_cam/image_matched', '/usb_cam/image_overlapped', '/usb_cam/image_stitched'])
            ]
        )
        stitch_topics = self.get_parameter('stitch_topics')
        publish_topics = self.get_parameter('publish_topics')

        # PUBLISHER
        matched_publisher = self.create_publisher(Image, publish_topics.value[0], 1)
        overlapped_publisher = self.create_publisher(Image, publish_topics.value[1], 1)
        stitched_publisher = self.create_publisher(Image, publish_topics.value[2], 1)

        # DEPENDENCIES
        logger = self.get_logger()
        bridge = CvBridge()
        feature_matcher = OmniGlueFeatureMatcher()
        # feature_matcher = CV2FeatureMatcher()

        # STITCHER
        stitcher = MultiCamStitcher(logger, matched_publisher, overlapped_publisher, stitched_publisher, bridge, feature_matcher)

        # SUBSCRIBERS
        stitch_subs = [
            Subscriber(
                self,
                Image,
                topic,
            )
            for topic
            in stitch_topics.value
        ]
        synchronizer = ApproximateTimeSynchronizer(stitch_subs, 10, 0.2)
        synchronizer.registerCallback(stitcher.image_callback)

# MAIN
def main(args=None):
    init(args=args)
    node = ROSNode()
    spin(node)
    node.destroy_node()
    shutdown()


if __name__ == '__main__':
    main()