import re
from collections import OrderedDict

from setuptools import setup


with open('README.rst', 'rt', encoding='utf8') as f:
    readme = f.read()

with open('aiokoa/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

setup(
    name='aiokoa',
    version=version,
    url='https://github.com/zeromake/aiokoa',
    project_urls=OrderedDict((
        # ('Documentation', ''),
        ('Code', 'https://github.com/zeromake/aiokoa'),
        ('Issue tracker', 'https://github.com/zeromake/aiokoa/issues'),
    )),
    license='MIT',
    author='zeromake',
    author_email='a390720046@gmail.com',
    maintainer='zeromake',
    maintainer_email='a390720046@gmail.com',
    long_description=readme,
    packages=['aiokoa'],
    platforms='any',
    python_requires='>=3.6',
    install_requires=[
        'httptools>=0.0.11',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: aiokoa',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
