from ultralytics import YOLO
model = YOLO("yolov8n.pt")
results = model.train(data="/home/louisdinhh/agilex_ws/yolo_training/project.yaml", epochs=100, imgsz=640, device="cuda")