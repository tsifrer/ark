import re
from codecs import open

import setuptools


with open('ark/__init__.py', 'r') as f:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE
    ).group(1)
if not version:
    raise RuntimeError('Cannot find version information')

with open('README.rst', 'r') as f:
    readme = f.read()

setuptools.setup(
    name='ark',
    version=version,
    description='Python implementation of Ark Blokchain.',
    long_description=readme,
    long_description_content_type='text/x-rst',
    author='tsifrer',
    url='https://github.com/tsifrer/ark',
    packages=['ark'],
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
