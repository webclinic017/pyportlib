from dependency_injector import providers, containers

from pyportlib import Position


class PositionContainer(containers.DeclarativeContainer):
    position = providers.Factory(Position)
