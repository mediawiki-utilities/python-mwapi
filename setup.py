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
    license=__license__,  # noqa
    packages=["mwapi"],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=["requests", "aiohttp"]
)
