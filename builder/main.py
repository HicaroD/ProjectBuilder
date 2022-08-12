from dataclasses import dataclass
from typing import Optional
import subprocess
import requests
import json
import os


class Repository:
    def __init__(self):
        try:
            self.name = self.get_project_name()
            self.description = self.get_project_description()
            self.license_name = self.get_license_name()
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

    def get_exact_license_keyword(self) -> str:
        # TODO: build a hash table to get the exact license keyword for the API call
        # See https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository#searching-github-by-license-type
        # Ex.:
        # "apache": ("Apache license 2.0", "apache-2.0")
        # the first member of the tuple is the original name for the README and the second
        # will be useful for the API request in order to generate a LICENSE file.
        pass

    def create_local_repository(self) -> None:
        subprocess.call(
            ["./builder/scripts/create_repository.sh", self.name, self.repository_link]
        )

    async def create_repository_on_github(self) -> None:
        # TODO: setup license template name
        data = {
            "name": self.name,
            "description": self.description,
            "private": self.is_private,
            "license_template": "mit",
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

    # TODO: create readme file template for the project
    def add_readme_template(self) -> None:
        with open(os.path.join(self.name, "README.md"), "a") as readme:
            readme.write(f"\n## License\nThis project is licensed under the {self.license_name.upper()} license. See [LICENSE](LICENSE).")


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
