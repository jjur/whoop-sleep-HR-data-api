from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="whoop-data",
    version="1.0.0",
    author="Juraj Vasek",
    author_email="your.email@example.com",
    description="A library to extract sleep and heart rate data from Whoop WebApp API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/whoop-sleep-HR-data-api",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.15.0",
        "pydantic>=2.0.0",
    ],
) 