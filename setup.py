"""Module for installing as package."""

from setuptools import find_packages, setup

with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="social-notion",
    version="0.0.1",
    packages=find_packages(),
    install_requires=requirements,
)
