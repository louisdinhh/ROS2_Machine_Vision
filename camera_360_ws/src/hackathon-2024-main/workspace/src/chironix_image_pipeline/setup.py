from setuptools import setup

package_name = "chironix_image_pipeline"

setup(
    name=package_name,
    version="0.0.0",
    packages=[package_name],
    install_requires=["setuptools", "rclpy"],
    zip_safe=True,
    maintainer="Technical Chironix",
    maintainer_email="chironix.technical@chironix.com",
    description="Chironix Image Pipeline packages",
    license="Proprietary",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "charuco_calibrator_node = chironix_image_pipeline.charuco_calibrator_node:main",
        ],
    },
)
