from os.path import join
from app import api
from app.utils import get_repository_name, to_json, write_json, read_json, create_if_not_exists
from abc import abstractmethod


class Generator:
    _api: api.Api

    def __init__(self, name: str, api: api.Api):
        self.name = name
        self._api = api

    @abstractmethod
    def generate(self, config, path):
        """
        Generates static files based on the supplied config to the specified path.

        Args:
                config (dict): The configuration for the generator
                path (str): The path to generate the static files to
        """
        raise NotImplementedError


class ReleaseGenerator(Generator):
    def __init__(self, api):
        super().__init__("release", api)

    def generate(self, config, path):
        path = join(path, "release")

        repositories = config["repositories"]

        for repository in repositories:
            release = self._api.get_release(repository)
            repository_name = get_repository_name(repository)

            tag = release["tag"]

            release_path = join(path, repository_name)
            release_json = to_json(release)

            create_if_not_exists(release_path)

            write_json(release_json, join(
                release_path, f"{tag}.json"), overwrite=False)
            write_json(
                release_json, join(release_path, "latest.json")
            )  # Overwrite the latest release

            # At last join the current tag to an index file
            index_path = join(path, f"{repository_name}.json")

            index = read_json(index_path, [])
            if tag not in index:  # TODO: Check if there a better way to do this
                index.append(tag)  # Add the current tag to the index

            write_json(index, index_path)


class ContributorGenerator(Generator):
    def __init__(self, api):
        super().__init__("contributor", api)

    def generate(self, config, path):
        path = join(path, "contributor")

        create_if_not_exists(path)
        repositories = config["repositories"]

        for repository in repositories:
            repository_name = get_repository_name(repository)

            contributors = self._api.get_contributor(repository)
            contributors_path = join(path, f"{repository_name}.json")

            write_json(contributors, contributors_path)


class SocialGenerator(Generator):
    def __init__(self, api):
        super().__init__("social", api)

    def generate(self, config, path):
        new_social = config["socials"]

        social_path = join(path, f"social.json")

        write_json(new_social, social_path)


class TeamGenerator(Generator):
    def __init__(self, api):
        super().__init__("team", api)

    def generate(self, config, path):
        organization = config["organization"]

        team = self._api.get_members(organization)

        team_path = join(path, f"team.json")

        write_json(team, team_path)


class DonationGenerator(Generator):
    def __init__(self, api):
        super().__init__("donation", api)

    def generate(self, config, path):
        donation = config["links"]

        donation_path = join(path, f"donation.json")

        write_json(donation, donation_path)


class GeneratorProvider:
    generators: list[Generator]

    def __init__(self, generators: list[Generator]):
        self.generators = generators

    def get(self, name: str) -> Generator | None:
        for generator in self.generators:
            if generator.name == name:
                return generator

        return None


class DefaultGeneratorProvider(GeneratorProvider):
    def __init__(self):
        self._api = api.GitHubApi()

        super().__init__([
            ReleaseGenerator(self._api),
            ContributorGenerator(self._api),
            SocialGenerator(self._api),
            TeamGenerator(self._api),
            DonationGenerator(self._api)
        ])
