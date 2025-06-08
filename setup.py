from setuptools import setup, find_packages

setup(
    name='orchestratex',
    version='0.1.0',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[
        'pytest>=7.0.0',
        'pytest-cov>=4.0.0',
        'coverage>=6.0.0',
        'pytest-asyncio>=0.21.0',
        'pytest-mock>=3.10.0',
        'pytest-xdist>=3.0.0',
        'flake8>=5.0.0',
        'black>=23.0.0',
        'isort>=5.10.1',
        'mypy>=1.0.0',
        'pylint>=2.17.0',
        'safety>=2.3.0',
        'bandit>=1.7.5',
        'sphinx>=6.0.0',
        'sphinx-rtd-theme>=1.2.0',
        'sphinx-autodoc-typehints>=1.22.0',
        'sphinxcontrib-apidoc>=0.3.0',
        'tox>=4.0.0',
        'bump2version>=1.0.1',
        'wheel>=0.40.0',
        'setuptools>=68.0.0'
    ],
    python_requires='>=3.8',
    include_package_data=True,
)
