FROM osrf/ros:humble-desktop-full

# APT INSTALL DEPENDENCIES
RUN apt-get update && apt-get install -y \
ros-humble-usb-cam \
ros-humble-tf-transformations \
python3-pip
RUN python3 -m pip install --upgrade pip

# INSTALL MULTI-CAM CALIBRATION DEPENDENCIES
RUN apt-get install -y \
cmake libgoogle-glog-dev libgflags-dev \
libatlas-base-dev \
libeigen3-dev \
libsuitesparse-dev \
libboost-all-dev \
wget
WORKDIR /ceres
RUN wget http://ceres-solver.org/ceres-solver-2.2.0.tar.gz
RUN tar zxf ceres-solver-2.2.0.tar.gz && \
    mkdir ceres-bin
WORKDIR /ceres/ceres-bin
RUN cmake ../ceres-solver-2.2.0 -DUSE_CUDA=OFF
RUN make -j3
RUN make test
RUN make install

# INSTALL MULTI-CAM CALIBRATION
WORKDIR /
RUN git clone https://github.com/rameau-fr/MC-Calib.git
WORKDIR /MC-Calib
RUN sed -i 's/6X6/4X4/g' McCalib/include/McCalib.hpp apps/create_charuco_boards/src/create_charuco_boards.cpp
RUN mkdir build
WORKDIR /MC-Calib/build
RUN cmake -DCMAKE_BUILD_TYPE=Release ..
RUN make -j10

# INSTALL OMNIGLUE
WORKDIR /
RUN git clone https://github.com/google-research/omniglue.git
WORKDIR /omniglue/models
RUN git clone https://github.com/rpautrat/SuperPoint.git && \
    mv SuperPoint/pretrained_models/sp_v6.tgz . && rm -rf SuperPoint && \
    tar zxvf sp_v6.tgz && rm sp_v6.tgz && \
    wget https://dl.fbaipublicfiles.com/dinov2/dinov2_vitb14/dinov2_vitb14_pretrain.pth && \
    wget https://storage.googleapis.com/omniglue/og_export.zip && \
    apt-get install -y unzip && \
    unzip og_export.zip && rm og_export.zip
WORKDIR /omniglue
RUN pip3 install -e .
ENV PYTHONPATH="${PYTHONPATH}:/omniglue"
RUN pip3 install "numpy<1.24"

# SETUP ENTRYPOINT
WORKDIR /setup
COPY ./ros-entrypoint.sh ./ros-entrypoint.sh
RUN chmod +x ros-entrypoint.sh

WORKDIR /workspace
ENTRYPOINT [ "/setup/ros-entrypoint.sh" ]
CMD ["bash"]