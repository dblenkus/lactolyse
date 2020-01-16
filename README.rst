=========
Lactolyse
=========

|build| |pypi_version| |pypi_pyversions| |pypi_downloads| |code_style|

.. |build| image:: https://travis-ci.org/dblenkus/lactolyse.svg?branch=master
    :target: https://travis-ci.org/dblenkus/lactolyse
    :alt: Build Status

.. |pypi_version| image:: https://img.shields.io/pypi/v/lactolyse.svg
    :target: https://pypi.org/project/lactolyse
    :alt: Version on PyPI

.. |pypi_pyversions| image:: https://img.shields.io/pypi/pyversions/lactolyse.svg
    :target: https://pypi.org/project/lactolyse
    :alt: Supported Python versions

.. |pypi_downloads| image:: https://pepy.tech/badge/lactolyse
    :target: https://pepy.tech/project/lactolyse
    :alt: Number of downloads from PyPI

.. |code_style| image:: https://img.shields.io/badge/code%20style-black-black.svg
    :target: https://black.readthedocs.io/
    :alt: Code style: black


Development
===========

This project requires Docker for running analysis and dependencies. If you
are not familiar with it, follow the `official tutorial`_.

To install the package in the development (editable) mode, first clone the
repository:

.. code-block:: bash

   $ git@github.com:dblenkus/lactolyse.git
   $ cd lactolyse

You should create and activate a fresh virtual environment for this project:

.. code-block:: bash

   $ python3 -m venv --prompt lactolyse .venv
   $ source .venv/bin/activate

And then install it with pip:

.. code-block:: bash

   $ python -m pip install -e .

Test project is in the ``tests`` directory, so you should run the rest of
commands in there:

.. code-block:: bash

   $ cd tests

First start Docker containers for PostgreSQL and Redis services:

.. code-block:: bash

   $ docker-compose up -d

Then, if you are setting up the environment for the first time, prepare the
database:

.. code-block:: bash

   $ ./manage.py migrate
   $ ./manage.py createsuperuser

And finally run the development server and background worker (in two separate
terminals):

.. code-block:: bash

   $ ./manage.py runserver
   $ ./manage.py runworker lactolyse.runanalysis


.. _official tutorial: https://www.docker.com/get-started
