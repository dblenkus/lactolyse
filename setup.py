#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Open source dataflow package for Django framework.
See:
https://github.com/genialis/resolwe
"""

from setuptools import find_packages, setup
# Use codecs' open for a consistent encoding
from os import path

base_dir = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(base_dir, 'README.rst')) as f:
    long_description = f.read()

# Get package metadata from 'lactolyse.__about__.py' file
about = {}
with open(path.join(base_dir, 'lactolyse', '__about__.py')) as f:
    exec(f.read(), about)

setup(
    name=about['__title__'],

    version=about['__version__'],

    description=about['__summary__'],
    long_description=long_description,

    url=about['__url__'],

    author=about['__author__'],
    author_email=about['__email__'],

    license=about['__license__'],

    # exclude tests from built/installed package
    packages=find_packages(exclude=['tests', 'tests.*', '*.tests', '*.tests.*']),
    package_data={
        'lactolyse': [
            'static/lactolyse/css/*.css',
            'templates/*.html',
            'templates/lactolyse/*.html',
            'templates/lactolyse/latex/*.tex',
        ],
    },
    install_requires=[
        'asgiref~=2.1',
        'channels~=2.1.0',
        'channels_redis~=2.1.0',
        'Django~=2.0.0',
        'django-material~=1.2.2',
        'docker~=3.0.0',
        'Jinja2~=2.10',
        'numpy~=1.14.0',
        'psycopg2-binary~=2.7.0',

    ],
    python_requires='>=3.6, <3.8',
    extras_require={
        'package': [
            'twine',
            'wheel',
        ],
        'test': [
            'check-manifest',
            'coverage>=4.2',
            'isort',
            'pycodestyle~=2.4.0',
            'pydocstyle~=2.1.1',
            'pylint~=1.9.1',
            'readme_renderer',
        ],
    },

    classifiers=[
        'Development Status :: 4 - Beta',

        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Other Audience',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: Apache Software License',

        'Operating System :: OS Independent',

        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='ftp lactate threshold',
)
