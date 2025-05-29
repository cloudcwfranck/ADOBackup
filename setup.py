from setuptools import setup, find_packages

setup(
    name="adobackup",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "azure-devops>=7.1.0b4",
        "azure-storage-blob>=12.17.0",
        "python-dotenv>=1.0.0",
        "questionary>=2.1.0"
    ],
    entry_points={
        "console_scripts": [
            "adobackup=adobackup.cli:main"
        ]
    },
    python_requires=">=3.8"
)