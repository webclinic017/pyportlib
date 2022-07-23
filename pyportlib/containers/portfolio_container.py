from dependency_injector import providers, containers

from pyportlib import Portfolio
from services.cash_manager import CashManager
from services.fx_rates import FxRates
from services.transaction_manager import TransactionManager


class PortfolioContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    transaction_manager = providers.Factory(TransactionManager)
    cash_manager = providers.Factory(CashManager)
    fx = providers.Factory(FxRates)

    ptf = providers.Factory(Portfolio)
