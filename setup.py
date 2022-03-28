from setuptools import find_packages, setup

import versioneer

setup(
    name="explotracker",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Exploratory experiment artifact tracker with filesystem storage (fs, s3fs, ...)",
    author="augustoamerico",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "pickle",
        "sys",
        "importlib",
        "os",
        "gzip",
        "io",
        "typing",
    ],
    extras_require={
        "s3fs": ["s3fs>=0.4.2"],
        "dev": ["versioneer"]
    }
)