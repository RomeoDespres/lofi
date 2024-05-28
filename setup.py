from __future__ import annotations

from pathlib import Path

from setuptools import find_packages, setup

name = "lofi"
here = Path(__file__).absolute().parent
requirements_path = here / "requirements.txt"
dev_requirements_path = here / "requirements_dev.txt"


def get_requirements(path: Path) -> list[str]:
    return path.read_text().splitlines()


setup(
    author="Roméo Després",
    maintainer="RomeoDespres",
    name=name,
    version="1.0.0",
    packages=find_packages(),
    install_requires=get_requirements(requirements_path),
    extras_require={"dev": get_requirements(dev_requirements_path)},
    include_package_data=True,
    entry_points={"console_scripts": [f"{name} = {name}.cli:main"]},
)
