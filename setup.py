from setuptools import setup, find_packages

setup(
    name="simisa",
    version="0.0.1b0",
    packages=find_packages(),
    install_requires=[
    ],
    author="Peter Grønbæk Andersen",
    author_email="peter@grnbk.io",
    description="A Python module to read and write files used with MSTS and Open Rails.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/pgroenbaek/simisa",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    license="GNU General Public License v3 or later (GPLv3+)",
)