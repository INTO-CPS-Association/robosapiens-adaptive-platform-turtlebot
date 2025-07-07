from setuptools import setup, find_packages

setup(
    name='lidarocclusion',
    version='0.0.1',
    description='a pip-installable package example',
    license='',
    packages=find_packages(include=["lidarocclusion", "lidarocclusion.*"]),
    author='Thomas Wright',
    author_email='thomas.wright@ece.au.dk',
    keywords=[],
    install_requires=[
        "portion",
        # ("pytest", "8.3.5"),
        "pytest",
        "scipy"
    ],
    url='https://github.com/twright/Lidar-Occlusion'
)
