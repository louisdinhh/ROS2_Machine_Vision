#!/bin/bash

source /opt/ros/humble/setup.bash
test -f /workspace/install/setup.bash && source /workspace/install/setup.bash
exec "$@"