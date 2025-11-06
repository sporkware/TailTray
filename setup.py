#!/usr/bin/env python3
"""
Setup script for TailTray
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="tailtray",
    version="0.1.0",
    author="TailTray Contributors",
    author_email="tailtray@example.com",
    description="Tailscale GUI for Linux - System tray application for KDE Plasma",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tailtray",
    packages=find_packages(),
    py_modules=['tailscale_client', 'tailtray_config'],
    scripts=['tailtray.py'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: System :: Networking",
        "Topic :: Desktop Environment :: K Desktop Environment (KDE)",
    ],
    keywords="tailscale vpn network gui kde plasma",
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    data_files=[
        ('share/applications', ['tailtray.desktop']),
        ('share/doc/tailtray', ['README.md', 'CHANGELOG.md', 'STATUS.md']),
        ('share/licenses/tailtray', ['LICENSE']),
    ],
    include_package_data=True,
    zip_safe=False,
)