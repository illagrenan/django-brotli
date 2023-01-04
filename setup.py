#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io

from setuptools import setup

setup(
    name="django-brotli",
    version="0.2.1",
    description="""Middleware that compresses response using brotli algorithm.""",
    long_description=io.open("README.rst", "r", encoding="utf-8").read(),
    url="https://github.com/illagrenan/django-brotli",
    license="MIT",
    author="Vasek Dohnal",
    author_email="vaclav.dohnal@gmail.com",
    packages=["django_brotli"],
    install_requires=["Django", "brotli>=1.0.0"],
    python_requires="~=3.6",
    include_package_data=True,
    zip_safe=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
