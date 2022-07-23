from dependency_injector import providers, containers

from pyportlib.position.position import Position


class PositionContainer(containers.DeclarativeContainer):
    position = providers.Factory(Position)
