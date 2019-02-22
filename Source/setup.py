import setuptools

with open('../README.md', 'r') as rm:
    long_description = rm.read()

setuptools.setup(
    name="PyBoy",
    version="0.0.1",
    author="Mads Ynddal",
    author_email="mads-pyboy@ynddal.dk",
    long_description=long_description,
    content_type="text/markdown",
    url="https://github.com/Baekalfen/PyBoy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "License :: Freely Distributable",
        "Operating System :: OS Independent",
        "Topic :: System :: Emulators",
    ],
    install_requires=[
        "pysdl2",
        "imageio",
        "numpy==1.10.0",
    ],
    dependency_links=[
        'git+https://bitbucket.org/pypy/numpy.git@4f9778cd49a48096f97cf85116b8820f3da6f80a#egg=numpy-1.10.0',
    ]
)
