import configparser
from pathlib import Path


def test_init_app_installs_django_for_generation_commands():
    config = configparser.ConfigParser()
    config.read(Path(__file__).resolve().parents[1] / "setup.cfg")

    requirements = "\n".join(
        config["options"]["install_requires"].strip().splitlines()
    ).lower()

    assert "django>=4.2,<6.0" in requirements


def test_package_version_is_stable_major_release():
    config = configparser.ConfigParser()
    config.read(Path(__file__).resolve().parents[1] / "setup.cfg")

    assert config["metadata"]["version"] == "3.0.0"
    classifiers = "\n".join(config["metadata"]["classifiers"].splitlines())
    assert "Development Status :: 5 - Production/Stable" in classifiers
