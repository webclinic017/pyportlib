from datetime import datetime
from pandas._libs.tslibs.offsets import BDay
from data_sources.data_reader import DataReader
import pandas as pd
from utils import logger


class Position(object):

    def __init__(self, ticker: str, currency: str, datareader: DataReader):
        self.ticker = ticker
        self.currency = currency
        self.datareader = datareader
        self._prices = pd.Series()
        self._quantities = pd.Series()
        self._load_prices()

    def __repr__(self):
        return f"{self.ticker}"

    def _load_prices(self):
        self._prices = self.datareader.read_prices(ticker=self.ticker).astype(float).sort_index()

    def get_prices(self):
        return self._prices

    def set_prices(self, prices: pd.Series) -> None:
        self._prices = prices

    def get_quantities(self) -> pd.Series:
        return self._quantities

    def set_quantities(self, quantities: pd.Series) -> None:
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
            prices = self.get_prices().loc[search_date:end_date]
            quantities = self.get_quantities()
            diff = prices.loc[prices.index.isin(quantities.index)].diff().dropna()
        except KeyError:
            raise KeyError("pnl error")

        base_pnl = diff.multiply(quantities.loc[search_date:end_date]).dropna().loc[start_date:end_date]
        pnl = pd.DataFrame(columns=['unrealized', 'realized', 'dividend', 'total'], index=base_pnl.index)
        pnl['unrealized'] = base_pnl
        pnl = pnl.fillna(0)

        if not transactions.empty:
            transactions.reset_index(inplace=True)
            ptf_currency = list(fx.keys())[1][3:]
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
                    pnl.loc[trx.Date, 'unrealized'] = (daily_avg_cost - self._prices.loc[trx.Date]) * new_qty * trx_fx
                elif trx.Type == 'Sell':
                    realized = (daily_avg_cost - (trx.Price * trx_fx)) * trx.Quantity
                    pnl.loc[trx.Date, 'realized'] += realized

                elif trx.Type == 'Dividend':
                    pnl.loc[trx.Date, 'dividend'] = trx.Price * trx_fx

                pnl.loc[:, 'total'] = pnl[['unrealized', 'realized', 'dividend']].sum(axis=1)
                pnl.loc[trx.Date, 'total'] -= trx.Fees
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