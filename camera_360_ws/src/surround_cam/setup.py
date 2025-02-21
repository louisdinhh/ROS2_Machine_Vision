from setuptools import setup

package_name = 'surround_cam'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/surround_cam.launch.py']),
        #('share/' + package_name + '/launch', ['launch/top_down_view.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Alexander',
    maintainer_email='alexander@example.com',
    description='A package for stitching rectified images into a surround image',
    license='Apache License 2.0',
    entry_points={
        'console_scripts': [
            'surround_cam = surround_cam.surround_merger:main',
        ],
    },
)