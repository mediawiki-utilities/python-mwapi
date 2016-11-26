import os.path

from setuptools import setup

about_path = os.path.join(os.path.dirname(__file__), "mwapi/about.py")
exec(compile(open(about_path).read(), about_path, "exec"))

setup(
    name=__name__,  # noqa
    version=__version__,  # noqa
    author=__author__,  # noqa
    author_email=__author_email__,  # noqa
    description=__description__,  # noqa
    url=__url__,  # noqa
    packages=["mwapi"],
    license=open("LICENSE").read(),
    long_description=open("README.md").read(),
    install_requires=["requests"]
)
