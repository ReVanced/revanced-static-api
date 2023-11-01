from os.path import join
from app import api
from app.utils import get_repository_name, to_json, write_json, read_json, create_if_not_exists
from abc import ABC, abstractmethod
from dependency_injector.wiring import Provide, inject
from app.dependencies import ApiContainer

class Generator(ABC):
    _api: api.Api | None

    def __init__(self, name: str, api: api.Api | None = None):
        """
        Args:
                name (str): The name of the generator
                api (Api | None): An optional api to use for the generator.
        """
        self.name = name
        self._api = api

    @abstractmethod
    async def generate(self, config, path):
        """
        Generates static files based on the supplied config to the specified path.

        Args:
                config (dict): The configuration for the generator
                path (str): The path to generate the static files to
        """
        raise NotImplementedError


class ReleasesGenerator(Generator):
    """
    Generates a release file for each repository in the config:
        - releases/<repository>/<tag>.json: Release information of the repository.
        - releases/<repository>/latest.json: Latest release information of the repository.
        - releases/<repository>.json: Index file containing all releases of the repository.
    """

    _api: api.Api

    @inject
    def __init__(self, api: api.Api = Provide[ApiContainer.api]):
        super().__init__("releases", api)

    async def generate(self, config, path):
        path = join(path, "releases")

        repositories = config["repositories"]

        for repository in repositories:
            release = await self._api.get_release(repository)
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
    Generates a contributor file for each repository in the config:
        - contributors/<repository>.json: Contributors of the repository.
    """
   
    _api: api.Api

    @inject
    def __init__(self, api: api.Api = Provide[ApiContainer.api]):
        super().__init__("contributors", api)

    async def generate(self, config, path):
        path = join(path, "contributors")

        create_if_not_exists(path)
        repositories = config["repositories"]

        for repository in repositories:
            repository_name = get_repository_name(repository)

            contributors = await self._api.get_contributor(repository)
            contributors_path = join(path, f"{repository_name}.json")

            write_json(contributors, contributors_path)


class ConnectionsGenerator(Generator):
    """
    Generates a file containing the connections of the organization:
        - connections.json: Connections of the organization.
    """

    def __init__(self):
        super().__init__("connections", None)

    async def generate(self, config, path):
        new_connections = config["connections"]

        connections_path = join(path, f"connections.json")

        write_json(new_connections, connections_path)


class TeamGenerator(Generator):
    """
    Generates a team file containing the members of the organization:
        - team.json: Members of the organization.
    """
   
    _api: api.Api

    @inject
    def __init__(self, api: api.Api = Provide[ApiContainer.api]):
        super().__init__("team", api)

    async def generate(self, config, path):
        organization = config["organization"]

        team = await self._api.get_members(organization)

        team_path = join(path, f"team.json")

        write_json(team, team_path)


class DonationsGenerator(Generator):
    """
    Generates a donation file containing ways to donate to the organization:
        - donations.json: Links and wallets to donate to the organization.
    """

    def __init__(self):
        super().__init__("donations")

    async def generate(self, config, path):
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


class AnnouncementGenerator(Generator):
    """
    Generates announcement files:

        - /announcements.json: Get a list of announcements from all channels.
        - /announcements/<channel>.json: Get a list of announcement from a channel.
        - /announcements/latest.json: Get the latest announcement.
        - /announcements/<channel>/latest.json: Get the latest announcement from a channel.
    """

    def __init__(self):
        super().__init__("announcements")

    async def generate(self, config, path):
        new_announcement = config["announcement"]
        new_announcement_channel = new_announcement["channel"]

        announcements_path = join(path, f"announcements.json")
        announcements = read_json(announcements_path, [])

        # Determine the id of the new announcement. The id is the highest id + 1
        new_announcement_id = 0
        for announcement in announcements:
            if announcement["id"] >= new_announcement_id:
                new_announcement_id = announcement["id"] + 1
        new_announcement["id"] = new_announcement_id

        # Add the new announcement to the list of announcements
        announcements.append(new_announcement)
        write_json(announcements, announcements_path)

        # Add the new announcement to the channel file
        channel_path = join(
            path, f"announcements/{new_announcement_channel}.json")
        create_if_not_exists(channel_path)
        channel_announcements = read_json(channel_path, [])
        channel_announcements.append(new_announcement)
        write_json(channel_announcements, channel_path)

        # Update the latest announcement file
        write_json(new_announcement, join(path, "announcements/latest.json"))

        # Update the latest announcement for the channel
        write_json(new_announcement, join(
            path, f"announcements/{new_announcement_channel}/latest.json"))


class RemoveAnnouncementGenerator(Generator):
    """
    Removes an announcement.
    """

    def __init__(self):
        super().__init__("remove_announcement")

    async def generate(self, config, path):
        # TODO: Implement this
        pass

class GeneratorProvider:
    """
    Provides a way to get a generator by name.
    """
    _generators = {}

    def __init__(self, generators: list[Generator]):
        """
        Args:
                generators (list[Generator]): A list of generators.
        """
        for generator in generators:
            self._generators[generator.name] = generator

    def get(self, name: str) -> Generator | None:
        """
        Gets a generator by name.

        Args:
                name (str): The name of the generator.

        Returns:
                Generator | None: The generator if found, otherwise None.
        """
        return self._generators[name] if name in self._generators else None

class DefaultGeneratorProvider(GeneratorProvider):
    def __init__(self):
        super().__init__(
            [
                ReleasesGenerator(),
                ContributorsGenerator(),
                TeamGenerator(),
                ConnectionsGenerator(),
                DonationsGenerator()
            ]
        )

class AnnouncementsGeneratorProvider(GeneratorProvider):
    def __init__(self):
        super().__init__(
            [
                AnnouncementGenerator(),
                RemoveAnnouncementGenerator()
            ]
        )