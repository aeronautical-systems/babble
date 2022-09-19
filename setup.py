#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.md') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', 'Lark', 'python-Levenshtein']

test_requirements = ['pytest>=3', ]

setup(
    author="Torsten Irländer",
    author_email='torsten.irlaender@googlemail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Simple package for natural language understanding (NLU)",
    entry_points={
        'console_scripts': [
            'babble-nlp=babble.nlp.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='babble',
    name='babble',
    packages=find_packages(include=['babble', 'babble.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/toirl/babble',
    version='0.1.0',
    zip_safe=False,
)
