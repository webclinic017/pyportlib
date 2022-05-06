#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Portofolio: Portfolio analytics and stock data daba management
https://github.com/phil-lo/PortoFolio
Portofolio manages your stock data, transactions and allows for easy portfolio creation
and analytics.
"""

from setuptools import setup, find_packages
import io
from os import path

# --- df version ---
with open("pyportlib/version.py") as f:
    line = f.read().strip()
    version = line.replace("version = ", "").replace('"', '')
# --- /df version ---

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with io.open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with io.open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.rstrip() for line in f]

setup(
    name='pyportlib',
    version=version,
    description='Streamlines backtesting and portfolio performance tracking with one tool',
    long_description=long_description,
    url='https://github.com/phil-lo/pyportlib',
    author='Philippe Lacroix-Ouellette',
    author_email='philippe.lacroix.ouellette@gmail.com',
    license='MIT License',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',

        'Operating System :: OS Independent',

        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Science/Research',

        'Topic :: Office/Business :: Financial',
        'Topic :: Office/Business :: Financial :: Investment',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',

        # 'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],

    platforms=['any'],
    keywords="""quant algotrading algorithmic-trading quantitative-trading
                quantitative-analysis algo-trading visualization plotting""",
    packages=find_packages(exclude=['docs', 'examples']),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'sample=sample:main',
        ],
    },

    include_package_data=True,
)
