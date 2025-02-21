from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'chironix_camera'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
        (os.path.join('share', package_name, 'calibrations'), glob(os.path.join('calibrations', '*.yaml'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='tom.matthews@chironix.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'multi_camera_capture = chironix_camera.multi_camera_capture:main',
            'multi_camera_stitcher = chironix_camera.multi_camera_stitcher:main',
        ],
    },
)
