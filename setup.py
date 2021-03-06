import setuptools

with open("requirements.txt") as f:
    requirements = [x.strip() for x in f]

setuptools.setup(
    name="cvs",
    version="1.0",
    author="Pavel Slabikov",
    author_email="author@example.com",
    description="Simple git realization",
    long_description="",
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
