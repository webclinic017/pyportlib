from datetime import datetime
from pandas._libs.tslibs.offsets import BDay
from .data_sources.data_reader import DataReader
import pandas as pd
from .utils import logger


class Position(object):

    def __init__(self, ticker: str, local_currency: str):
        self.ticker = ticker.upper()
        self.currency = local_currency.upper()
        self._datareader = DataReader()
        self._prices = pd.Series()
        self._quantities = pd.Series()
        self._load_prices()
        self._fundamentals = {'balance_sheet': pd.DataFrame(),
                              'cash_flow': pd.DataFrame(),
                              'income_statement': pd.DataFrame()}

    def __repr__(self):
        return f"{self.ticker} - {self.currency}"

    def update_prices(self):
        self._datareader.update_prices(ticker=self.ticker)
        self._load_prices()
        logger.logging.info(f'{self} prices updated with local currency')

    def _load_prices(self):
        self._prices = self._datareader.read_prices(ticker=self.ticker).astype(float).sort_index()

    def get_fundamentals(self, statement_type: str):
        if not self._fundamentals.get(statement_type).empty:
            return self._fundamentals.get(statement_type)
        else:
            self._fundamentals[statement_type] = self._datareader.read_fundamentals(ticker=self.ticker,
                                                                                    statement_type=statement_type)
            return self._fundamentals.get(statement_type)

    @property
    def prices(self):
        return self._prices

    @prices.setter
    def prices(self, prices: pd.Series) -> None:
        self._prices = prices

    @property
    def quantities(self) -> pd.Series:
        if not self._quantities.empty:
            return self._quantities
        else:
            return pd.Series(index=self._prices.index, data=[1 for _ in range(len(self._prices))])

    @quantities.setter
    def quantities(self, quantities: pd.Series) -> None:
        self._quantities = quantities

    def daily_pnl(self,
                  start_date: datetime = None,
                  end_date: datetime = None,
                  transactions: pd.DataFrame = pd.DataFrame(),
                  fx: dict = None) -> pd.DataFrame:
        """
        gives all pnl of position in $ amount
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
                    logger.logging.info(
                        f'{self.ticker}: error in trx date ({trx.Date}), NYSE market not open. open qty set to 0')
                    start_qty = 0

                trx_fx = fx.get(f"{trx.Currency}{ptf_currency}").loc[trx.Date]
                daily_avg_cost = self._prices.shift(1).loc[trx.Date]

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
