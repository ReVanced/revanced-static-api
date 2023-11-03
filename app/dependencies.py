from dependency_injector import providers, containers

from app.api import GitHubApi


class ApiContainer(containers.DeclarativeContainer):
    api = providers.Singleton(GitHubApi)


def wire_dependencies():
    ApiContainer().wire(modules=["app.generator"])
