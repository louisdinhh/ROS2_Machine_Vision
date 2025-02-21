from setuptools import find_packages
from setuptools import setup

setup(
    name='chironix_image_pipeline',
    version='0.0.0',
    packages=find_packages(
        include=('chironix_image_pipeline', 'chironix_image_pipeline.*')),
)
