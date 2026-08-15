#!/usr/bin/env python3
"""Luanti Builder - setup.py for pip install"""
from setuptools import setup, find_packages

setup(
    name="luanti-builder",
    version="1.0.0",
    description="自然语言生成 Luanti/Minetest 建筑 — 跨平台 GUI 工具",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="MichaelQiu",
    license="MIT",
    url="https://github.com/cpufreestyle/luanti-builder",
    packages=find_packages(),
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "luanti-builder=lb_pkg.server:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment",
    ],
)
