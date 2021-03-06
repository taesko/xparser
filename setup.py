# !/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import sys
from shutil import rmtree

from setuptools import setup, Command

# Package meta-data.
NAME = 'xparser'
PACKAGE_NAME = 'xrp'
DESCRIPTION = 'An XResources parser for python applications.'
KEYWORDS = 'parser XResources'
URL = 'https://github.com/taesko/xparser'
EMAIL = 'taeskow@gmail.com'
AUTHOR = 'Antonio Todorov'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = None

REQUIRED_FOR_INSTALL = []

here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

# try to convert github markdown to restructured text because PyPI does not support the former
# don't crash because this file is executed during installation through setup.py and not just during upload to PyPI
try:
    import pypandoc
    long_description = pypandoc.convert(source=long_description, to='rst', format='markdown_github')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    long_description = ""
except OSError:
    print("warning: pandoc is not installed on this system - could not convert Markdown to RST")
    long_description = ""
except Exception as e:
    print("warning: an unkown exception occurred while converting documentation to RST:")
    print(e.args)
    long_description = ""

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    with open(os.path.join(here, 'src', PACKAGE_NAME, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag -a v{0} -m "version {0}"'.format(about['__version__']))
        os.system('git push --tags')

        sys.exit()


class TestUploadCommand(Command):
    """Support setup.py test_upload."""

    description = 'Build and publish the package to TestPyPI.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel distribution…')
        os.system('{0} setup.py sdist bdist_wheel'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload --repository-url https://test.pypi.org/legacy/ dist/*')

        sys.exit()


setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    keywords=KEYWORDS,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    python_requires=REQUIRES_PYTHON,
    packages=['xrp'],
    package_dir={'': 'src'},
    install_requires=REQUIRED_FOR_INSTALL,
    tests_require=['pytest', 'pytest-runner'],
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Framework :: Pytest'

    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
        'test_upload': TestUploadCommand
    },
)
