import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="covidmx",
    version="0.3.1",
    author="Federico Garza",
    author_email="fede.garza.ramirez@gmail.com",
    description="Python API to get information about COVID-19 in México.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FedericoGarza/covidmx",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    install_requires = [
        "more-itertools>=6.0.0",
        "pandas>=0.25.2",
        "Unidecode>=1.1.1",
        "requests>=2.21.0",
        "xlrd>=1.2.0",
        "mapsmx>=0.0.3",
        "matplotlib>=3.0.3",
        "mapclassify>=2.2.0",
        "descartes>=1.1.0",

    ]
)
