from dataclasses import dataclass
from typing import Optional


class Project:
    def __init__(self):
        try:
            self.name = self.get_project_name()
            self.description = self.get_project_description()
            self.license_name = self.get_license_name()
        except KeyboardInterrupt:
            print("\nError while trying to get project information")
            exit(1)

    def get_project_name(self) -> str:
        name = input("What is the project name? ").strip()
        if name == "":
            raise ValueError("Project must have a name")
        return name

    def get_project_description(self) -> str:
        description = input("What is the project description? ").strip()
        if description == "":
            raise ValueError("Project must have a description")
        return description

    def get_license_name(self) -> Optional[str]:
        license_name = input("(OPTIONAL) What is the project license? ").strip()
        if license_name == "":
            return None
        return license_name


class Builder:
    def __init__(self, project: Project):
        self.project = project

    def build(self):
        try:
            print(self.project.name)
            print(self.project.description)
            print(self.project.license_name)

        except Exception as e:
            print(e)
            exit(1)


def main():
    project = Project()
    builder = Builder(project)
    builder.build()
