from setuptools import find_packages, setup

package_name = 'panorama_cam'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/panorama_cam.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='louisdinhh',
    maintainer_email='louisdinhh@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'panorama_node = panorama_cam.panorama_node:main',
        ],
    },
)
