# 🚀 User Guide

Welcome to this repository! This collection of ROS workspaces was created to explore and implement key concepts in **computer vision**, **sensor calibration**, and **sensor fusion** for robotics and autonomous systems. Each workspace focuses on a specific topic, providing a hands-on environment for learning, experimentation, and practical implementation.

---

# 📚 Repository Overview

The repository consists of five independent workspaces, each covering an essential aspect of robotic perception and vision.

## 📷 Camera Calibration

### 🎯 Objective
Learn the fundamentals of camera calibration by estimating **intrinsic** and **extrinsic** camera parameters using ROS calibration tools.

### 📖 Topics Covered
- Camera intrinsic parameters
- Camera extrinsic parameters
- Chessboard-based camera calibration
- ROS camera calibration tools
- Image rectification

---

## 📸 Camera-Camera Calibration

### 🎯 Objective
Master the process of calibrating multiple cameras to determine their relative positions and orientations.

### 📖 Topics Covered
- Multi-camera calibration
- Camera synchronization
- Relative pose estimation
- Coordinate frame transformations
- Stereo and multi-camera alignment

---

## 📷🔗📡 Camera-LiDAR Calibration

### 🎯 Objective
Integrate camera and LiDAR sensors into a common coordinate frame for accurate sensor fusion.

### 📖 Topics Covered
- Camera-LiDAR extrinsic calibration
- Point cloud projection
- Image and LiDAR alignment
- Sensor fusion concepts
- Point cloud visualization

---

## 🌍 Camera 360

### 🎯 Objective
Work with 360-degree camera systems to capture, stitch, and process panoramic imagery.

### 📖 Topics Covered
- Panoramic image processing
- Image stitching
- 360° camera workflows
- Omnidirectional vision
- Panorama visualization

---

## 🤖🎯 YOLOv8 Functionality Testing

### 🎯 Objective
Evaluate and test the core functionalities of the YOLOv8 object detection framework within a ROS environment.

### 📖 Topics Covered
- Object detection
- Model inference
- ROS integration
- Detection visualization
- Performance testing

---

# 🎯 Repository Goals

This repository aims to:

- 📚 Build a strong foundation in camera calibration.
- 🔄 Understand multi-sensor calibration and sensor fusion.
- 🤖 Explore perception pipelines for robotics.
- 🧪 Provide reusable ROS workspaces for experimentation.
- 🚀 Serve as a reference for future robotics and computer vision projects.

---

# 📂 Repository Structure

```text
.
├── camera_calibration/
├── camera_camera_calibration/
├── camera_lidar_calibration/
├── camera_360/
├── yolov8_testing/
└── README.md
```

Each workspace is self-contained with its own source code, launch files, and documentation.

---

# 🚀 Getting Started

1. Clone this repository.
2. Navigate to the desired workspace.
3. Build the workspace using `colcon build`.
4. Source the workspace:
   ```bash
   source install/setup.bash
   ```
5. Follow the workspace-specific documentation to run the examples.

---

Happy coding! 🚀
