import os
import sys
from setuptools import setup, find_packages

# Read requirements
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read README
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='optimus-cline',
    version='1.0.0',
    description='VSCode extension integration for AI assistance',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Lance James',
    author_email='lance@221b.sh',
    url='https://github.com/lancejames221b/optimus-cline',
    packages=find_packages(exclude=['tests*']),
    install_requires=requirements,
    python_requires='>=3.9',
    entry_points={
        'console_scripts': [
            'optimus-cline=assistant.__main__:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Tools',
    ],
    keywords='vscode extension ai assistant development tools',
    project_urls={
        'Bug Reports': 'https://github.com/lancejames221b/optimus-cline/issues',
        'Source': 'https://github.com/lancejames221b/optimus-cline',
        'Documentation': 'https://github.com/lancejames221b/optimus-cline/docs',
    },
    package_data={
        'optimus_cline': [
            'templates/*',
            'docs/*',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    options={
        'bdist_wheel': {
            'universal': True
        }
    },
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'isort>=5.0.0',
            'mypy>=1.0.0',
            'pylint>=2.0.0',
        ],
        'docs': [
            'sphinx>=7.0.0',
            'sphinx-rtd-theme>=1.0.0',
            'sphinx-autodoc-typehints>=1.0.0',
        ],
    }
)
