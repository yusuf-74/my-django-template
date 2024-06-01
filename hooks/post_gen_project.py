from __future__ import print_function

import os
import random
import shutil

import toml
import yaml

try:
    # Inspired by
    # https://github.com/django/django/blob/master/django/utils/crypto.py
    random = random.SystemRandom()
    using_sysrandom = True
except NotImplementedError:
    using_sysrandom = False


TERMINATOR = "\x1b[0m"
WARNING = "\x1b[1;33m [WARNING]: "
INFO = "\x1b[1;33m [INFO]: "
HINT = "\x1b[3;33m"
SUCCESS = "\x1b[1;32m [SUCCESS]: "


def no_docker():
    # Remove Dockerfile and docker-compose.[any].yml files
    shutil.rmtree("Dockerfile", ignore_errors=True)
    shutil.rmtree("docker-compose", ignore_errors=True)


def no_celery():
    # Remove celery.py file
    shutil.rmtree("{{cookiecutter.project_slug}}/celery.py", ignore_errors=True)
    try:
        with open("{{cookiecutter.project_slug}}/__init__.py", "w") as f:
            f.write("")

        with open("{{cookiecutter.project_slug}}/settings.py", "r+") as f:
            lines = f.readlines()
            f.seek(0)
            for line in lines:
                if "celery" not in line.lower():
                    f.write(line)
            f.truncate()
    except FileNotFoundError:
        print(f"{WARNING}No __init__.py file found. Skipping removing celery imports")
        pass

    # remove celery containers from docker-compose.[any].yml
    # grab the docker-compose files
    docker_compose_files = [
        f for f in os.listdir() if f.startswith("docker-compose") and f.endswith(".yml")
    ]
    for docker_compose_file in docker_compose_files:
        with open(docker_compose_file, "r") as f:
            docker_compose = yaml.safe_load(f)
        new_services = {}
        for service in docker_compose["services"]:
            if (
                "beat" not in service
                and "worker" not in service
                and "redis" not in service
                and "flower" not in service
            ):
                new_services[service] = docker_compose["services"][service]

        with open(docker_compose_file, "w") as f:
            yaml.dump(new_services, f)
    try:
        env_example_files = [
            f for f in os.listdir("env_files") if f.endswith(".env.example")
        ]
    except Exception:
        print(
            f"{WARNING}No env_files folder found. Skipping removing celery environment variables"
        )
        env_example_files = []
    for env_example_file in env_example_files:
        with open(env_example_file, "r+") as f:
            lines = f.readlines()
            f.seek(0)
            for line in lines:
                if "celery_" not in line.lower():
                    f.write(line)
            f.truncate()


def no_nginx():
    # Remove nginx folder
    shutil.rmtree("nginx", ignore_errors=True)

    # Remove nginx container from docker-compose.[any].yml
    # grab the docker-compose files
    docker_compose_files = [
        f for f in os.listdir() if f.startswith("docker-compose") and f.endswith(".yml")
    ]
    for docker_compose_file in docker_compose_files:
        with open(docker_compose_file, "r") as f:
            docker_compose = yaml.safe_load(f)
        new_services = {}
        for service in docker_compose["services"]:
            if "nginx" not in service:
                new_services[service] = docker_compose["services"][service]

        with open(docker_compose_file, "w") as f:
            yaml.dump(new_services, f)


def no_bitbucket_pipeline():
    # Remove bitbucket-pipelines.yml file
    shutil.rmtree("bitbucket-pipelines.yml", ignore_errors=True)


def no_pre_commit():
    # Remove .pre-commit-config.yaml file
    shutil.rmtree(".pre-commit-config.yaml", ignore_errors=True)
    shutil.rmtree(".flake8", ignore_errors=True)
    try:
        # remove black and isort from pyproject.toml
        with open("pyproject.toml", "r+") as f:
            pyproject = toml.load(f)
            pyproject["tool"]["black"] = None
            pyproject["tool"]["isort"] = None
            toml.dump(pyproject, f)
    except FileNotFoundError:
        print(
            f"{WARNING}No pyproject.toml file found. Skipping removing black and isort"
        )


def main():
    if "{{cookiecutter.use_docker}}" == "n":
        no_docker()
        print(f"{SUCCESS}Removed Dockerfile and docker-compose files")

    if "{{cookiecutter.use_celery}}" == "n":
        no_celery()
        print(f"{SUCCESS}Removed celery.py and celery containers")

    if "{{cookiecutter.use_nginx}}" == "n":
        no_nginx()
        print(f"{SUCCESS}Removed nginx folder and nginx container")

    if "{{cookiecutter.use_bitbucket_pipeline}}" == "n":
        no_bitbucket_pipeline()
        print(f"{SUCCESS}Removed bitbucket-pipelines.yml file")

    if "{{cookiecutter.use_pre_commit}}" == "n":
        no_pre_commit()
        print(f"{SUCCESS}Removed .pre-commit-config.yaml file")


if __name__ == "__main__":
    main()
