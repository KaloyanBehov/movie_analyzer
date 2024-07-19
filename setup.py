from setuptools import setup, find_packages

setup(
    name="movie_analyzer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
    ],
    entry_points={
        "console_scripts": [
            "movie_analyzer=movie_analyzer.main:main",
        ],
    },
    author="Kaloyan Behov",
    description="A Python program to analyze movie data from CSV files",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)