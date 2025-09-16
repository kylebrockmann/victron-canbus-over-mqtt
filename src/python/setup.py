import setuptools
import yaml

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("build.yml", "r") as yml_fd:
    parameters = yaml.load(yml_fd, Loader=yaml.FullLoader)
    setup_parameters = parameters["python"]

setuptools.setup(
    **setup_parameters,
    packages=setuptools.find_packages(
        exclude=["t", "t.*"],
    ),
    install_requires=requirements
)
