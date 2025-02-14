from ultralytics import YOLO
import cv2

# Load YOLOv8 model (pre-trained on COCO dataset)
model = YOLO('yolov8n.pt')  # 'yolov8n.pt' is the smallest model

# Open webcam or video file
cap = cv2.VideoCapture(0)  # Change to video file path if needed

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Perform inference
    results = model(frame)
    
    # Draw bounding boxes
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = box.conf[0].item()
            cls = int(box.cls[0].item())
            label = model.names[cls]
            
            # Only show people (class 0 in COCO dataset)
            if label == 'person':
                # Bounding box color (red)
                color = (85, 85, 255)
                thickness = 2

                # Draw rectangle
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

                # Label text
                text = f"{label} {conf:.1f}"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                font_thickness = 1

                # Get text size
                text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
                text_x, text_y = x1, y1 - 10  # Position above the bounding box

                # Draw background rectangle for text
                cv2.rectangle(frame, (text_x, text_y - text_size[1] - 5), 
                              (text_x + text_size[0], text_y + 5), color, -1)

                # Put text
                cv2.putText(frame, text, (text_x, text_y), font, font_scale, 
                            (255, 255, 255), font_thickness, cv2.LINE_AA)
    
    # Show the frame
    cv2.imshow('YOLOv8 Person Detection', frame)
    
    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
