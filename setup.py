"""
PyProfiler - Simple, Powerful Python Profiling
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="pyprofiler",
    version="1.0.0",
    author="Sankalp Patidar",
    author_email="patidarsankalp@gmail.com",
    description="Lightweight, zero-dependency profiling for Python applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Baavro/pyprofiler",
    packages=find_packages(exclude=["tests", "examples"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Zero dependencies!
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "pyprofiler-analyze=pyprofiler.cli:main",
        ],
    },
    include_package_data=True,
    keywords=[
        "profiling",
        "performance",
        "timing",
        "benchmark",
        "optimization",
        "monitoring",
        "debugging",
    ],
    project_urls={
        "Bug Reports": "https://github.com/Baavro/pyprofiler/issues",
        "Source": "https://github.com/Baavro/pyprofiler",
        "Documentation": "https://github.com/Baavro/pyprofiler#readme",
    },
)