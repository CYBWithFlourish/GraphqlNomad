from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="graphqlnomad",
    version="1.0.0",
    author="CYBWithFlourish",
    author_email="project.samclak@gmail.com",
    description="An integrated tool to detect, fingerprint, and explore GraphQL endpoints.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CYBWithFlourish/GraphQLNomad",
    packages=find_packages(),
    install_requires=[
        "requests",
        "colorama",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache 2.0 License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Security",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'graphqlnomad=graphqlnomad.nomad:main',
        ],
    },
)
