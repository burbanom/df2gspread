#!/usr/bin/env python
# Author: "Eduard Trott" <etrott@redhat.com>

# python-2.7 setup.py build

from __future__ import absolute_import, unicode_literals

from setuptools import setup

VERSION_FILE = "df2gspread/_version.py"
VERSION_EXEC = ''.join(open(VERSION_FILE).readlines())
__version__ = ''
exec(VERSION_EXEC)  # update __version__
if not __version__:
    raise RuntimeError("Unable to find version string in %s." % VERSION_FILE)

# acceptable version schema: major.minor[.patch][-sub[ab]]
__pkg__ = 'df2gspread'
__pkgdir__ = {'df2gspread': 'df2gspread',
                'gspread2df': 'df2gspread'}
__pkgs__ = ['df2gspread']
__desc__ = 'Export tables to Google Spreadsheets.'
__irequires__ = [
    # CORE DEPENDENCIES
    'argparse==1.3.0',
    'google-api-python-client==1.4.1',
    'gspread==0.2.5',
    'oauth2client>=1.4.12',
    'pandas==0.16.2',
]
__xrequires__ = {
    'tests': [
        'pytest==2.7.2',
        # 'instructions',
        # 'pytest-pep8==1.0.6',  # run with `py.test --pep8 ...`
    ],
    # 'docs': ['sphinx==1.3.1', ],
    # 'github': ['PyGithub==1.25.2', ],
    # 'invoke': ['invoke==0.10.1', ],
}

pip_src = 'https://pypi.python.org/packages/src'
__deplinks__ = []

# README is in the parent directory
readme_pth = 'README.rst'
with open(readme_pth) as _file:
    readme = _file.read()

github = 'https://github.com/etrott/df2gspread'
download_url = '%s/archive/master.zip' % github

default_setup = dict(
    url=github,
    license='GPLv3',
    author='Eduard Trott',
    author_email='etrott@redhat.com',
    maintainer='Chris Ward',
    maintainer_email='cward@redhat.com',
    download_url=download_url,
    long_description=readme,
    data_files=[],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Topic :: Office/Business',
        'Topic :: Utilities',
    ],
    keywords=['information'],
    dependency_links=__deplinks__,
    description=__desc__,
    install_requires=__irequires__,
    extras_require=__xrequires__,
    name=__pkg__,
    package_dir=__pkgdir__,
    packages=__pkgs__,
    version=__version__,
    zip_safe=False,
)

setup(**default_setup)