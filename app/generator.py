from os.path import join
from app import api
from app.utils import get_repository_name, to_json, write_json, read_json, create_if_not_exists
from abc import abstractmethod

class Generator:
    _api: api.Api

    def __init__(self, name: str, api: api.Api | None = None):
        """
        Args:
                name (str): The name of the generator
                api (Api | None): An optional api to use for the generator.
        """
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


class ReleasesGenerator(Generator):
    """
    Generates a release file for each repository in the config.
    The release file is named after the tag of the release and contains the latest release information of the repository.
    A `latest.json` file is also generated containing the latest release of the repository.
    """

    def __init__(self, api):
        super().__init__("releases", api)

    def generate(self, config, path):
        path = join(path, "releases")

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


class ContributorsGenerator(Generator):
    """
    Generates a contributor file for each repository in the config.
    The contributor file is named after the repository and contains the contributors of the repository.
    """

    def __init__(self, api):
        super().__init__("contributors", api)

    def generate(self, config, path):
        path = join(path, "contributors")

        create_if_not_exists(path)
        repositories = config["repositories"]

        for repository in repositories:
            repository_name = get_repository_name(repository)

            contributors = self._api.get_contributor(repository)
            contributors_path = join(path, f"{repository_name}.json")

            write_json(contributors, contributors_path)


class ConnectionsGenerator(Generator):
    """
    Generates a file containing the connections of the organization.
    """

    def __init__(self, api):
        super().__init__("connections", api)

    def generate(self, config, path):
        new_connections = config["connections"]

        connections_path = join(path, f"connections.json")

        write_json(new_connections, connections_path)


class TeamGenerator(Generator):
    """
    Generates a team file containing the members of the organization.
    """

    def __init__(self, api):
        super().__init__("team", api)

    def generate(self, config, path):
        organization = config["organization"]

        team = self._api.get_members(organization)

        team_path = join(path, f"team.json")

        write_json(team, team_path)


class DonationsGenerator(Generator):
    """
    Generates a donation file containing ways to donate to the organization.
    """

    def __init__(self, api):
        super().__init__("donations", api)

    def generate(self, config, path):
        links = config["links"] if "links" in config else []
        wallets = config["wallets"] if "wallets" in config else []

        donation_path = join(path, f"donations.json")

        write_json(
            {
                "links": links,
                "wallets": wallets
            },
            donation_path
        )


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
            ReleasesGenerator(self._api),
            ContributorsGenerator(self._api),
            ConnectionsGenerator(self._api),
            TeamGenerator(self._api),
            DonationsGenerator(self._api)
        ])
