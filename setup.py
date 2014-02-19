from strings import Template
from setuptools import setup, find_packages

version = '1.0'
long_description = """$README

Contributors
============
$CONTRIBUTORS

Changes
=======
$CHANGES
"""


setup(
    name='edeposit.amqp.aleph',
    version=version,
    description="E-Deposit AMQP module for communication with Aleph",
    long_description=Template(long_description).substitute(
        README=open('README.txt').read(),
        CONTRIBUTORS=open('CONTRIBUTORS.txt').read(),
        CHANGES=open('CHANGES.txt').read()
    ),

    url='https://github.com/jstavel/edeposit.amqp.aleph',

    author='Edeposit team',
    author_email='',

    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: GNU General Public License (GPL)"
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    # keywords='' ,
    license='GPL',

    packages=find_packages('src'),
    package_dir={'': 'src'},

    namespace_packages=[
        'edeposit',
        'edeposit.amqp'
    ],
    include_package_data=True,

    zip_safe=False,
    install_requires=[
        'setuptools'
        "pyDHTMLParser>=1.7.4, <2.0.0",
        "httpkie>=1.1.0, <2.0.0",
    ],
    extras_require={
        "test": [
            "unittest2",
            "robotsuite",
            "mock",
            "robotframework-httplibrary"
        ],
        "docs": [
            "sphinxcontrib-robotdoc",
            "sphinx",
        ]
    }
)
