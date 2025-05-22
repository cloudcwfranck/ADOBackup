from setuptools import setup, find_packages

setup(
    name="adobackup",
    version="1.0.0",
    packages=find_packages(),
    install_requires=open('requirements.txt').read().splitlines(),
    entry_points={
        'console_scripts': [
            'adobackup=src.cli:main'
        ]
    },
    include_package_data=True,
    python_requires='>=3.8',
)