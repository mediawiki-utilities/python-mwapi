from setuptools import setup

setup(
        name="python-mwapi",
        version="0.1.1",
        author="Yuvi Panda",
        author_email="yuvipanda@gmail.com",
        url="http://github.com/yuvipanda/python-mwapi",
        packages=["mwapi", ],
        license="MIT License",
        description = "Simple wrapper for the Mediawiki API",
        long_description = open("README").read(),
        install_requires = ["requests"]
)
