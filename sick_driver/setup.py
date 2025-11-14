from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'sick_driver'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['tests', 'tests.*']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    extras_require={
        'test': ['pytest', 'mock']  # Testing dependencies
    },
    zip_safe=True,
    maintainer='dma',
    maintainer_email='dma@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'lidar_driver = sick_driver.lidar_driver:main',
        ],
    },
)

