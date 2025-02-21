#!/bin/bash

/MC-Calib/build/apps/calibrate/calibrate /workspace/src/chironix_camera/config/multi_camera_calibration_config.yml
python3 /workspace/src/chironix_camera/chironix_camera/extrinsic_results_to_transform.py
