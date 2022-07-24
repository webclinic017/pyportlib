from dependency_injector import providers, containers

from pyportlib.portfolio.portfolio import Portfolio


class PortfolioContainer(containers.DeclarativeContainer):
    ptf = providers.Factory(Portfolio)
