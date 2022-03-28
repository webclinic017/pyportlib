from datetime import datetime
from pandas._libs.tslibs.offsets import BDay
from .data_sources.data_reader import DataReader
import pandas as pd
from .utils import logger


class Position(object):

    def __init__(self, ticker: str, local_currency: str = None, strategy: str = None):
        self.ticker = ticker.upper()
        self._strategy = strategy
        self._datareader = DataReader()
        self._prices = pd.Series()
        self._quantities = pd.Series()
        self._load_prices()

        if local_currency is None:
            self.currency = 'CAD' if ticker[-2:] == 'TO' else 'USD'
        else:
            self.currency = local_currency

    @property
    def name(self):
        return "position"

    @property
    def strategy(self):
        return self._strategy

    @strategy.setter
    def strategy(self, value: str):
        self._strategy = value

    def __repr__(self):
        return f"{self.ticker} - {self.currency} - {self.strategy}"

    def update_data(self, fundamentals_and_dividends: bool = False) -> None:
        """
        updates all of the position's market data
        :param fundamentals_and_dividends: True if you want to update
        fundamentals and dividends data
        :return: None
        """
        if fundamentals_and_dividends:
            self._update_fundamentals()
            self._update_dividends()
        self._update_prices()

    def _update_prices(self):
        self._datareader.update_prices(ticker=self.ticker)
        self._load_prices()
        logger.logging.info(f'{self} prices updated with local currency')

    def get_fundamentals(self, statement_type: str) -> pd.DataFrame:
        """
        retreives the position's fundamentals by statement type
        :param statement_type: choose from ('balance_sheet', 'cashflow', 'income_statement')
        :return: df with statement data
        """
        return self._datareader.read_fundamentals(ticker=self.ticker, statement_type=statement_type)

    def get_splits(self) -> pd.DataFrame:
        """
        retreives the position's stock splits
        :return:
        """
        return self._datareader.get_splits(ticker=self.ticker)

    def _update_dividends(self):
        self._datareader.update_dividends(ticker=self.ticker)
        logger.logging.info(f'{self} dividends updated with local currency')

    def _update_fundamentals(self):
        self._datareader.update_statement(ticker=self.ticker, statement_type='all')
        logger.logging.info(f'{self} statements updated with local currency')

    def dividends(self) -> pd.DataFrame:
        """
        retreives dividends of the position's stock
        :return:
        """
        return self._datareader.read_dividends(ticker=self.ticker)

    def _load_prices(self):
        self._prices = self._datareader.read_prices(ticker=self.ticker).astype(float).sort_index()

    def market_value(self, date: datetime) -> float:
        return self.prices.loc[date] * self.quantities.loc[date]

    def npv(self) -> pd.Series:
        return self.prices.multiply(self.quantities).dropna()

    @property
    def prices(self) -> pd.Series:
        return self._prices

    @prices.setter
    def prices(self, prices: pd.Series) -> None:
        self._prices = prices

    @property
    def quantities(self) -> pd.Series:
        if not self._quantities.empty:
            return self._quantities
        else:
            return pd.Series(index=self.prices.index, data=[1 for _ in range(len(self.prices))])

    @quantities.setter
    def quantities(self, quantities: pd.Series) -> None:
        self._quantities = quantities

    def daily_pnl(self,
                  start_date: datetime = None,
                  end_date: datetime = None,
                  transactions: pd.DataFrame = pd.DataFrame(),
                  fx: dict = None) -> pd.DataFrame:
        """
        gives the pnl of position in $ amount by type of pnl
        :param fx: dict of fx pairs for conversion if there are transactions
        :param transactions: transactions from a portfolio, if none transactions are not considered
        :param start_date: start date of series (if only param, end_date is last date)
        :param end_date: start date of series (if only param, end_date the only date given in series)
        :return: series of position pnl in $ amount
        """

        if end_date is None:
            end_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        if start_date is None:
            start_date = end_date

        search_date = start_date - BDay(4)
        try:
            prices = self.prices.loc[search_date:end_date]
            quantities = self.quantities
            diff = prices.loc[prices.index.isin(quantities.index)].diff().dropna()
        except KeyError:
            raise KeyError("pnl error")

        base_pnl = diff.multiply(quantities.loc[search_date:end_date]).dropna().loc[start_date:end_date]
        pnl = pd.DataFrame(columns=['unrealized', 'realized', 'dividend', 'total'], index=base_pnl.index)
        pnl['unrealized'] = base_pnl
        pnl = pnl.fillna(0)

        if not transactions.empty:
            transactions = transactions[:end_date].reset_index()
            ptf_currency = list(fx.keys())[0][3:]
            for trx_idx in range(len(transactions)):
                trx = transactions.iloc[trx_idx]
                try:
                    start_qty = self._quantities.shift(1).fillna(0).loc[trx.Date]
                except KeyError:
                    logger.logging.error(f'{self.ticker}: ({trx.Date}), NYSE market not open. open qty set to 0')
                    start_qty = 0

                trx_fx = fx.get(f"{trx.Currency}{ptf_currency}").loc[trx.Date]
                try:
                    daily_avg_cost = self._prices.shift(1).loc[trx.Date]
                except KeyError:
                    logger.logging.error(f'no data for {self.ticker}, pnl not computed')
                    break

                if trx.Type == 'Buy':
                    new_qty = (trx.Quantity + start_qty)
                    daily_avg_cost = (trx.Quantity * (trx.Price * trx_fx) + start_qty * daily_avg_cost) / new_qty
                    pnl.loc[trx.Date, 'unrealized'] = (self._prices.loc[trx.Date] - daily_avg_cost) * new_qty
                elif trx.Type == 'Sell':
                    realized = (daily_avg_cost - (trx.Price * trx_fx)) * trx.Quantity
                    pnl.loc[trx.Date, 'realized'] += realized

                elif trx.Type == 'Dividend':
                    pnl.loc[trx.Date, 'dividend'] = trx.Price * trx_fx
                pnl.loc[trx.Date, 'total'] -= trx.Fees
        pnl.loc[:, 'total'] = pnl[['unrealized', 'realized', 'dividend', 'total']].sum(axis=1)

        return pnl.fillna(0)

    def daily_total_pnl(self,
                        start_date: datetime = None,
                        end_date: datetime = None,
                        transactions: pd.DataFrame = pd.DataFrame(),
                        fx: dict = None) -> pd.DataFrame:
        """
        gives total pnl of position in $ amount
        :param fx: dict of fx pairs for conversion if there are transactions
        :param transactions: transactions from a portfolio, if none transactions are not considered
        :param start_date: start date of series (if only param, end_date is last date)
        :param end_date: start date of series (if only param, end_date the only date given in series)
        :return: series of position pnl in $ amount
        """
        total = self.daily_pnl(start_date=start_date, end_date=end_date, transactions=transactions, fx=fx)['total']
        return total
