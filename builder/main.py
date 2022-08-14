from typing import Optional
import subprocess
import requests
import json
import os

from licenses import LICENSES
from gitignore_templates import GITIGNORE_TEMPLATES


class Repository:
    def __init__(self):
        try:
            self.name = self.get_project_name()
            self.description = self.get_project_description()
            self.license_name = self.get_license_name()
            self.gitignore_template = self.get_gitignore_template()
            self.is_private = self.ask_if_repo_is_private()
            self.repository_link = None
            self.oauth_token = self.get_oauth_token()
        except KeyboardInterrupt:
            print("\nError while trying to get project information")
            exit(1)

    def get_oauth_token(self) -> str:
        home_dir = os.path.expanduser("~")
        oauth_token_file_path = os.path.join(home_dir, "project_builder.json")
        if not os.path.isfile(oauth_token_file_path):
            raise ValueError("'project_builder.json' was not found on home directory")

        with open(oauth_token_file_path) as json_file:
            token = json.loads(json_file.read())["token"]
            if token is None:
                raise ValueError("'project_builder' doesn't contain the token")
            return token

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

    def ask_if_repo_is_private(self) -> str:
        is_private = input("Is it a private repository? [y/n] ").strip()
        if is_private == "y":
            return "true"
        elif is_private == "n":
            return "false"
        else:
            raise ValueError(f"Invalid answer: {is_private}")

    def is_gitignore_template_avaiable(self) -> bool:
        return self.gitignore_template in GITIGNORE_TEMPLATES

    def get_gitignore_template(self) -> Optional[str]:
        license_name = input("(OPTIONAL) What is the .gitignore template? ").strip()
        if license_name == "":
            return None
        return license_name

    def is_license_avaiable(self) -> bool:
        return self.license_name in LICENSES

    def get_license(self) -> str:
        if not self.is_license_avaiable():
            raise ValueError(f"Invalid license name: {self.license_name}")
        return LICENSES[self.license_name]

    def create_local_repository(self) -> None:
        project_name = self.name.replace(" ", "_").lower()
        subprocess.call(
            [
                "./builder/scripts/create_repository.sh",
                project_name,
                self.repository_link,
            ]
        )

    async def create_repository_on_github(self) -> None:
        if not self.is_license_avaiable():
            raise ValueError(f"Invalid license name: {self.license_name}")

        if not self.is_gitignore_template_avaiable():
            raise ValueError(f"Invalid gitignore template: {self.gitignore_template}")

        data = {
            "name": self.name,
            "description": self.description,
            "private": self.is_private,
            "license_template": self.license_name,
            "gitignore_template": self.gitignore_template,
            "auto_init": "true",
        }
        headers = {
            "Authorization": f"token {self.oauth_token}",
            "Accept": "application/vnd.github+json",
        }
        request = requests.post(
            "https://api.github.com/user/repos", data=json.dumps(data), headers=headers
        )
        if not request:
            raise ValueError(
                f"Unable to create repository. Make sure you're credentials are correct and your repository name is not already in use."
            )

        self.repository_link = request.json()["svn_url"]

    def add_readme_template(self) -> None:
        original_license_name = self.get_license()
        project_folder = self.name.replace(" ", "_").lower()
        with open(os.path.join(project_folder, "README.md"), "a") as readme:
            readme.write(
                f"\n## License\nThis project is licensed under the {original_license_name}. See [LICENSE](LICENSE)."
            )


class Builder:
    def __init__(self, repository: Repository):
        self.repository = repository

    async def build(self) -> None:
        await self.repository.create_repository_on_github()
        self.repository.create_local_repository()
        self.repository.add_readme_template()


async def main():
    repository = Repository()
    builder = Builder(repository)
    await builder.build()
