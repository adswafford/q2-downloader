# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from setuptools import setup, find_packages

setup(
    name="q2-downloader",
    version='0.0.1',
    packages=find_packages(),
    author="EBI Downloader Development Team",
    author_email="yoshiki@ucsd.edu",
    description="Download data from ENA/SRA",
    license='BSD-3-Clause',
    url="https://qiime2.org",
    entry_points={
        'qiime2.plugins':
        ['q2-downloader=q2_downloader.plugin_setup:plugin']
    },
    zip_safe=False,
)
