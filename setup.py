# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='instamonitor',
    version="1.1",
    packages=find_packages(),
    author="shader69",
    install_requires=["requests", "argparse", "tabulate", "colorama"],
    description="ToFill",
    long_description="ToFill",
    include_package_data=True,
    url='https://github.com/shader69/instamonitor',
    entry_points={'console_scripts': ['instamonitor = instamonitor.__main__:main_for_setup']},
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
