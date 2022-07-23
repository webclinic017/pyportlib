from dependency_injector import containers, providers

from pyportlib.market_data_sources.yahoo_connection import YahooConnection
from pyportlib.services.data_reader import DataReader


class DataSourceContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    yahoo = providers.Singleton(YahooConnection)

    market_data_source = providers.Selector(config.market_data,
                                            yahoo=yahoo)

    statements_data_source = providers.Selector(config.statements,
                                                yahoo=yahoo)

    datareader = providers.Singleton(DataReader,
                                     market_data_source=market_data_source,
                                     statements_data_source=statements_data_source)