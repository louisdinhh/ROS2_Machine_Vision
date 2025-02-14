import cv2
import os
import sys

# Check if a base name was provided as a command-line argument
if len(sys.argv) > 1:
    base_name = sys.argv[1]
else:
    base_name = "image"  # Default base name if none is provided

# Open the webcam
cap = cv2.VideoCapture(0)  # 0 is the default camera, change to suit your camera

# Counter for saved images
img_counter = 0

# Check for existing files and find the next available number
while os.path.exists(f"{base_name}_{img_counter}.jpg"):
    img_counter += 1

print("Press 'SPACE' to capture an image or 'q' to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    # Show the live feed
    cv2.imshow("Camera", frame)

    # Capture key press
    key = cv2.waitKey(1)
    if key % 256 == 32:  # SPACE key
        # Save the image
        img_name = f"{base_name}_{img_counter}.jpg"
        cv2.imwrite(img_name, frame)
        print(f"{img_name} saved!")
        img_counter += 1
    elif key % 256 == 113:  # q key
        break

cap.release()
cv2.destroyAllWindows()

