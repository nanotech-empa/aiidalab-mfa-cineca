"""Setup script for aiidalab-mfa-cineca package."""
from setuptools import setup, find_packages

setup(
    name="aiidalab-mfa-cineca",
    version="0.1.0",
    description="AiiDAlab app for MFA authentication with CINECA HPC",
    author="nanotech-empa",
    author_email="",
    url="https://github.com/nanotech-empa/aiidalab-mfa-cineca",
    packages=find_packages(),
    install_requires=[
        "aiidalab>=21.0.0",
    ],
    python_requires=">=3.7",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
