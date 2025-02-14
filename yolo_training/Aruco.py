import cv2
import numpy as np
from pupil_apriltags import Detector

# Initialize AprilTag detector with better parameters
detector = Detector(
    families="tag36h11",
    quad_decimate=2.0,  # Adjust for performance vs. accuracy trade-off
    quad_sigma=0.0,      # 0 for default, increase for noisy images
    refine_edges=True    # Improve edge refinement for better accuracy
)

# Load camera matrix and distortion coefficients (after calibration)
# Example values, replace with your own calibration data
camera_matrix = np.array([[800, 0, 320], [0, 800, 240], [0, 0, 1]], dtype=np.float32)
dist_coeffs = np.array([0, 0, 0, 0], dtype=np.float32)  # Replace with real distortion values

# Open a connection to the webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Undistort image (for accurate detection)
    frame_undistorted = cv2.undistort(gray, camera_matrix, dist_coeffs)

    # Detect AprilTags
    detections = detector.detect(frame_undistorted)

    # Draw detected tags
    for detection in detections:
        corners = detection.corners.astype(int)

        # Estimate pose of the cube using the tag
        tag_size = 0.05  # Assuming each tag is 5 cm (adjust as needed)
        obj_points = np.array([
            [-tag_size / 2, -tag_size / 2, 0],
            [ tag_size / 2, -tag_size / 2, 0],
            [ tag_size / 2,  tag_size / 2, 0],
            [-tag_size / 2,  tag_size / 2, 0]
        ], dtype=np.float32)

        # SolvePnP to get rotation & translation vectors
        ret, rvec, tvec = cv2.solvePnP(obj_points, detection.corners, camera_matrix, dist_coeffs)

        if ret:
            # Draw cube projection
            cube_points = np.array([
                [-tag_size / 2, -tag_size / 2, 0],
                [ tag_size / 2, -tag_size / 2, 0],
                [ tag_size / 2,  tag_size / 2, 0],
                [-tag_size / 2,  tag_size / 2, 0],
                [-tag_size / 2, -tag_size / 2, tag_size],
                [ tag_size / 2, -tag_size / 2, tag_size],
                [ tag_size / 2,  tag_size / 2, tag_size],
                [-tag_size / 2,  tag_size / 2, tag_size]
            ], dtype=np.float32)

            img_points, _ = cv2.projectPoints(cube_points, rvec, tvec, camera_matrix, dist_coeffs)

            img_points = img_points.reshape(-1, 2).astype(int)

        # Display tag ID
        tag_id = str(detection.tag_id)
        cv2.putText(frame, f"ID: {tag_id}", tuple(corners[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    # Display the frame
    cv2.imshow("AprilTag Cube Detection", frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
