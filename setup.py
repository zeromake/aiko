# -*- coding: utf-8 -*-

import re
from collections import OrderedDict

from setuptools import setup


with open('README.rst', 'rt', encoding='utf8') as f:
    readme = f.read()

with open('aiko/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

setup(
    name='aiko',
    version=version,
    url='https://github.com/zeromake/aiko',
    project_urls=OrderedDict((
        # ('Documentation', ''),
        ('Code', 'https://github.com/zeromake/aiko'),
        ('Issue tracker', 'https://github.com/zeromake/aiko/issues'),
    )),
    license='MIT',
    author='zeromake',
    author_email='a390720046@gmail.com',
    maintainer='zeromake',
    maintainer_email='a390720046@gmail.com',
    long_description=readme,
    packages=['aiko'],
    platforms='any',
    python_requires='>=3.5',
    install_requires=[
        'httptools>=0.0.11',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
