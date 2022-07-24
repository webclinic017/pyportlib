from dependency_injector import providers, containers

from pyportlib.services.transaction import Transaction
from pyportlib.services.cash_change import CashChange
from pyportlib.services.cash_manager import CashManager
from pyportlib.services.fx_rates import FxRates
from pyportlib.services.transaction_manager import TransactionManager


class ServicesContainer(containers.DeclarativeContainer):
    transaction = providers.Factory(Transaction)
    cash_change = providers.Factory(CashChange)
    transaction_manager = providers.Factory(TransactionManager)
    cash_manager = providers.Factory(CashManager)
    fx = providers.Factory(FxRates)

