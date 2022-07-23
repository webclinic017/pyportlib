from datetime import datetime

from pyportlib.containers.services_container import ServicesContainer
from pyportlib.containers.datareader_container import DataReaderContainer
from pyportlib.containers.portfolio_container import PortfolioContainer
from pyportlib.containers.position_container import PositionContainer
from pyportlib.position.iposition import IPosition
from pyportlib.utils import config_utils

data_source_config = config_utils.data_source_config()

ptf_container = PortfolioContainer()
position_container = PositionContainer()
services_container = ServicesContainer()
datareader_container = DataReaderContainer(config=data_source_config)


def portfolio(account: str, currency: str):
    datareader = datareader_container.datareader()

    cash_manager = services_container.cash_manager(account=account)
    transaction_manager = services_container.transaction_manager(account=account)

    required_currencies = transaction_manager.get_currencies()

    fx = services_container.fx(ptf_currency=currency, currencies=required_currencies, datareader=datareader)

    ptf = ptf_container.ptf(account=account,
                            currency=currency,
                            cash_manager=cash_manager,
                            transaction_manager=transaction_manager,
                            fx=fx,
                            datareader=datareader)

    return ptf


def position(ticker: str, local_currency: str = None, tag: str = None) -> IPosition:
    datareader = datareader_container.datareader()

    position = position_container.position(ticker=ticker,
                                           local_currency=local_currency,
                                           tag=tag,
                                           datareader=datareader)

    return position


def transaction(date: datetime,
                ticker: str,
                transaction_type: str,
                quantity: int,
                price: float,
                fees: float,
                currency: str):
    trx = services_container.transaction(date=date,
                                         ticker=ticker,
                                         transaction_type=transaction_type,
                                         quantity=quantity,
                                         price=price,
                                         fees=fees,
                                         currency=currency)

    return trx


def cash_change(date: datetime, direction: str, amount: float):
    cc = services_container.cash_change(date=date,
                                        direction=direction,
                                        amount=amount)
    return cc
