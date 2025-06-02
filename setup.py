from setuptools import setup, find_packages

setup(
    name="adobackup",
    version="1.0.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    entry_points={
        'console_scripts': [
            'adobackup=adobackup.cli:main',
        ],
    },
    install_requires=[
        'azure-devops>=7.1.0b4',
        'azure-storage-blob>=12.0.0',
        'questionary>=2.0.0',
        'python-dotenv>=1.0.0'
    ],
    python_requires='>=3.8',
)