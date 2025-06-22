#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="terminal-logger",
    version="0.1.0",
    author="Terminal Logger Contributors",
    author_email="your.email@example.com",
    description="A utility that executes terminal commands and logs them to MongoDB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/terminal-logger",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "terminal-logger=terminal_logger:main",
            "query-history=query_history:main",
            "maintain-db=maintain_db:main",
            "vector-query=vector_query:main",
        ],
    },
    tests_require=[
        "pytest",
        "pytest-cov",
    ],
)
