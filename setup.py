# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="exception_handler_plus",
    version="0.1.0",
    description="Simple Exception Handler Decorator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",     # fixme add url
    author="Sergei Sazonov",
    author_email='sspytdev@gmail.com',
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent"
    ],
    packages=["exception_handler_plus"],
    include_package_data=True,
    install_requires=[]
)
