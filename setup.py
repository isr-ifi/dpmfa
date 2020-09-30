# -*- coding: utf-8 -*-
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dpmfa",
    version="1.1",
    author="ISR - UZH",
    author_email="goncalves@ifi.uzh.ch",
    description="Dynamic probabilistic material flow analysis simulator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/isr-ifi/dpmfa",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
