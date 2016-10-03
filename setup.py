#!/usr/bin/env python

from distutils.core import setup

from os.path import abspath, dirname, join

version_file = join(dirname(abspath(__file__)), 'src', 'NcclientLibrary', 'version.py')

with open(version_file) as file:
    code = compile(file.read(), version_file, 'exec')
    exec(code)

DESCRIPTION = """
Robot Framework keyword library wrapper NETCONF requests.
"""[1:-1]


CLASSIFIERS = """
Development Status :: 5 - Production/Stable
License :: Public Domain
Operating System :: OS Independent
Programming Language :: Python
Topic :: Software Development :: Testing
"""[1:-1]

setup(
    name         = 'robotframework-ncclient',
    version      = VERSION,
    description  = 'Robot Framework keyword library wrapper around ncclient',
    long_description = DESCRIPTION,
    author       = 'Mallikarjunarao Kosuri',
    author_email = 'venkatamallikarjunarao.kosuri@adtran.com',
    url          = 'http://github.com/vkosuri/robotframework-ncclient',
    license      = 'Public Domain',
    keywords     = 'robotframework testing test automation NETCONF client requests',
    platforms    = 'any',
    classifiers  = CLASSIFIERS.splitlines(),
    package_dir  = {'' : 'src'},
    packages     = ['NcclientLibrary'],
    package_data = {'NcclientLibrary': ['tests/*.robot']},
    requires=[
      'robotframework',
      'ncclient'
    ],
)
