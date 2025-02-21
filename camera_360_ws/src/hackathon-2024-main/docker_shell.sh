#!/bin/bash

xhost +local:docker
docker exec -it ros2-dev-container /setup/ros-entrypoint.sh bash
