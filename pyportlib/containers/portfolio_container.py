from dependency_injector import providers, containers

from pyportlib.portfolio.portfolio import Portfolio
from pyportlib.services.cash_manager import CashManager
from pyportlib.services.fx_rates import FxRates
from pyportlib.services.transaction_manager import TransactionManager


class PortfolioContainer(containers.DeclarativeContainer):
    transaction_manager = providers.Factory(TransactionManager)
    cash_manager = providers.Factory(CashManager)
    fx = providers.Factory(FxRates)

    ptf = providers.Factory(Portfolio)
