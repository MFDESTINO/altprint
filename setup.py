import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="altprint",
    version="0.1.2",
    author="couto0",
    author_email="daniel.couto64@gmail.com",
    description="Alternative 3d printing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/couto0/altprint",
    keywords='FFF FDM 3dprinting slicer slicing gcode',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['numpy>=1.19.4', 'Shapely>=1.7.1', 'trimesh>=3.9.1', 'PuLP>=2.4', 'scipy>=1.7.0', 'networkx>=2.5.1', 'rtree>=0.9.7'],
)
