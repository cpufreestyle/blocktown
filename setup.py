#!/usr/bin/env python3
"""Luanti Builder - setup.py for pip install"""
from setuptools import setup, find_packages

setup(
    name="blocktown",
    version="1.0.0",
    description="Blocktown — Luanti AI 工具套件：自然语言建筑生成 + AI 小镇",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="MichaelQiu",
    license="MIT",
    url="https://github.com/cpufreestyle/blocktown",
    packages=find_packages(),
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "blocktown=lb_pkg.server:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment",
    ],
)
