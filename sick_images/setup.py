from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'sick_images'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['tests', 'tests.*']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    extras_require={
        'test': ['pytest', 'mock']  # Testing dependencies
    },
    zip_safe=True,
    maintainer='Ben Cometto',
    maintainer_email='benjamin@cometto.org',
    description='Maps 2D points into 3D accumulated pointcloud',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'point_processor = sick_images.point_processor:main',
            'image_generator = sick_images.image_generator:main',
            'point_cloud_generator = sick_images.point_cloud_generator:main',
        ],
    },
)

