from containers.data_source_container import DataSourceContainer
from containers.portfolio_container import PortfolioContainer
from containers.position_container import PositionContainer
from utils import config_utils

data_source_config = config_utils.data_source_config()

ptf_container = PortfolioContainer()
position_container = PositionContainer()
datareader_container = DataSourceContainer(config=data_source_config)


def portfolio(account: str, currency: str):
    datareader = datareader_container.datareader()

    cash_manager = ptf_container.cash_manager(account=account)
    transaction_manager = ptf_container.transaction_manager(account=account)

    required_currencies = transaction_manager.get_currencies()

    fx = ptf_container.fx(ptf_currency=currency, currencies=required_currencies, datareader=datareader)

    ptf = ptf_container.ptf(account=account,
                            currency=currency,
                            cash_manager=cash_manager,
                            transaction_manager=transaction_manager,
                            fx=fx,
                            datareader=datareader)

    return ptf


def position(ticker: str, local_currency: str = None, tag: str = None):
    datareader = datareader_container.datareader()

    position = position_container.position(ticker=ticker,
                                           local_currency=local_currency,
                                           tag=tag,
                                           datareader=datareader)

    return position