from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'sick_conversion'

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
            'scan_to_cloud_converter = sick_conversion.scan_to_cloud_converter:main',
            'scan_to_3d_projector = sick_conversion.scan_to_3d_projector:main',
            'cloud_accumulator = sick_conversion.cloud_accumulator:main',
            'voxel_accumulator = sick_conversion.voxel_accumulator:main',
        ],
    },
)

