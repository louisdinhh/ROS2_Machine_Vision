import cv2
import numpy as np

# Define the camera devices
camera_1 = '/dev/video0'
camera_2 = '/dev/video2'

# Open video capture for each camera
cap1 = cv2.VideoCapture(camera_1)
cap2 = cv2.VideoCapture(camera_2)

# Set camera resolution for consistency
cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Check if cameras opened successfully
if not cap1.isOpened():
    print(f"Cannot open camera {camera_1}")
    exit()
if not cap2.isOpened():
    print(f"Cannot open camera {camera_2}")
    exit()

# Initialize the SIFT detector
sift = cv2.SIFT_create()

# Initialize a stabilized homography matrix
stabilized_H = None
alpha = 0.0001  # Smoothing factor (lower values stabilize more)

while True:
    # Capture frame-by-frame from each camera
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()

    if not ret1 or not ret2:
        print("Failed to grab frame from one of the cameras.")
        break

    # Detect keypoints and descriptors
    kp1, des1 = sift.detectAndCompute(frame1, None)
    kp2, des2 = sift.detectAndCompute(frame2, None)

    # Create a BFMatcher object with knn
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)

    # Match descriptors using knn
    matches = bf.knnMatch(des1, des2, k=2)

    # Apply ratio test to filter matches
    good_matches = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:  # Ratio test threshold
            good_matches.append(m)

    # Draw feature mappings
    feature_mappings = cv2.drawMatches(
        frame1, kp1, frame2, kp2, good_matches, None,
        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
    )
    cv2.imshow('Feature Mappings', feature_mappings)

    # Perform homography estimation
    if len(good_matches) > 4:
        pts1 = np.float32([kp1[m.queryIdx].pt for m in good_matches])
        pts2 = np.float32([kp2[m.trainIdx].pt for m in good_matches])

        H, mask = cv2.findHomography(pts1, pts2, cv2.RANSAC, 5.0)
        if H is not None:
            # Stabilize homography using exponential smoothing
            if stabilized_H is None:
                stabilized_H = H
            else:
                stabilized_H = alpha * H + (1 - alpha) * stabilized_H

            # Warp frame1 to align with frame2 using stabilized homography
            height, width = frame2.shape[:2]
            warped_frame1 = cv2.warpPerspective(frame1, stabilized_H, (width * 2, height))

            # Create a blank canvas for the panorama
            panorama = np.zeros((height, width * 2, 3), dtype=np.uint8)

            # Place frame2 on the canvas
            panorama[:height, :width] = frame2

            # Feathering: Create a mask for the overlap
            overlap_width = 200  # Adjust for smoother blending
            mask = np.zeros((height, overlap_width), dtype=np.float32)
            mask[:, :overlap_width] = np.linspace(0, 1, overlap_width)

            # Blend the overlapping region
            start_x = width - overlap_width
            for i in range(3):  # Iterate over color channels
                panorama[:, start_x:width, i] = (
                    warped_frame1[:, start_x:width, i] * mask[:, :overlap_width]
                    + frame2[:, start_x:width, i] * (1 - mask[:, :overlap_width])
                )

            # Fill in the remaining warped frame on the right
            panorama[:, width:] = warped_frame1[:, width:]

            # Display the stitched panorama
            cv2.imshow('Panorama', panorama)
        else:
            print("Homography estimation failed.")

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture objects
cap1.release()
cap2.release()

# Close all OpenCV windows
cv2.destroyAllWindows()
