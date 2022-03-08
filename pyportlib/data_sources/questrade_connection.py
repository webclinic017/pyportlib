from datetime import datetime
from typing import Union, List
import pandas as pd
from pandas._libs.tslibs.offsets import BDay
from .questrade_api.questrade import Questrade
import dateutil.parser
from ..helpers.transaction import Transaction
from ..portfolio import Portfolio
from ..position import Position
from ..utils import dates_utils


class QuestradeConnection(Questrade):
    def __init__(self, account_name, **kwargs):
        super().__init__(**kwargs)
        self.account_name = account_name

    def _get_account_id(self):
        accounts = self.accounts.get('accounts')
        tfsa_id = [acc for acc in accounts if acc.get('type') == self.account_name.upper() and acc.get('status') == 'Active'][0].get('number')
        return tfsa_id

    def get_positions(self):
        return self.account_positions(self._get_account_id())

    def get_balances(self):
        return self.account_balances(self._get_account_id())

    def get_transactions(self, start_date: datetime = None, end_date: datetime = None):

        if not end_date:
            end_date = datetime.now().replace(hour=0, minute=0, second=0,
                                              microsecond=0).astimezone().isoformat('T')

        date_rng = dates_utils.get_market_days(start=start_date, end=end_date)
        list_of_trx = []
        for date in date_rng:
            date = date.isoformat('T') + '-05:00'
            kwargs = {'startTime': date, 'endTime': date}
            trx = self.account_activities(self._get_account_id(), **kwargs).get('activities', self.account_activities(
                self._get_account_id(), **kwargs))
            if trx:
                list_of_trx.extend(trx)

        return list_of_trx

    def get_transactions_list(self, start_date: datetime = None, end_date: datetime = None) -> List[Transaction]:
        transactions = self.get_transactions(start_date, end_date)

        list_of_transactions = []
        for i in range(len(transactions)):
            trx = self._make_transaction(transactions[i])
            list_of_transactions.append(trx)

        to_remove = ['ARRY', "IPL.TO"]
        list_of_transactions = self._remove_transactions(
            [pos for pos in list_of_transactions if not isinstance(pos, str)], to_remove)
        return list_of_transactions

    def update_transactions(self, portfolio: Portfolio) -> None:
        last_trade = portfolio.transactions.index.max()
        list_of_transactions = self.get_transactions_list(start_date=last_trade)

        transactions = self.remove_duplicated_transaction(new_transactions=list_of_transactions,
                                                          ptf_transactions=portfolio.transactions,
                                                          last_trade_date=last_trade)
        portfolio.add_transaction(transactions)

    def remove_duplicated_transaction(self, new_transactions: List[Transaction], ptf_transactions: pd.DataFrame,
                                      last_trade_date: datetime):
        duped = self.duplicated_transaction(new_transactions=new_transactions,
                                            ptf_transactions=ptf_transactions,
                                            last_trade_date=last_trade_date)
        transactions = []
        for trx in new_transactions:
            merge = trx.get().merge(duped, indicator=True)
            if merge.empty:
                transactions.append(trx)
            else:
                pass

        return transactions

    @staticmethod
    def duplicated_transaction(new_transactions: List[Transaction], ptf_transactions: pd.DataFrame,
                               last_trade_date: datetime):
        transactions = pd.concat([trx.get() for trx in new_transactions])
        transactions = pd.concat([transactions, ptf_transactions], axis=0).sort_index().loc[last_trade_date:]
        duped = transactions.duplicated()
        return transactions.loc[duped]

    def _make_transaction(self, transaction) -> Union[Transaction, None]:
        if transaction.get('type') not in ['Trades', 'Dividends', 'Transfers']:
            return transaction.get('type')

        date = dateutil.parser.isoparse(transaction.get('tradeDate')).replace(hour=0, minute=0, second=0, microsecond=0,
                                                                              tzinfo=None)
        ticker = transaction.get('symbol')
        currency = transaction.get('currency')
        trx_type = transaction.get('type')
        qty = transaction.get('quantity')
        fees = abs(transaction.get('commission'))

        if not isinstance(ticker, float):
            pos = Position(ticker=ticker, local_currency=currency)
        else:
            return trx_type

        splits = pos.get_splits()
        split_factor = self._calc_split(splits=splits, trade_date=date)

        if trx_type == 'Dividends':
            trx_type = 'Dividend'
            price = transaction.get('netAmount')

        elif trx_type == "Trades":
            trx_type = transaction.get('action')
            price = transaction.get('price') / split_factor

        elif trx_type == 'Transfers':
            if transaction.get('quantity') == 0:
                return trx_type
            price = self._transfer_cost(position=pos, date=date)

        else:
            raise ValueError(f"error in transaction {date} {ticker}")

        trx = Transaction(date=date,
                          ticker=ticker,
                          type=trx_type,
                          quantity=qty * split_factor,
                          price=price,
                          fees=fees,
                          currency=currency)

        return trx

    @staticmethod
    def _calc_split(splits: pd.DataFrame, trade_date: datetime) -> float:
        if not isinstance(splits, list):
            if not splits.empty:
                splits = splits.loc[trade_date:].cumprod()
                try:
                    split_factor = splits.iloc[-1]
                except Exception:
                    split_factor = 1
            else:
                split_factor = 1
        else:
            split_factor = 1

        return split_factor

    @staticmethod
    def _transfer_cost(position: Position, date: datetime) -> float:
        try:
            price = position.prices.loc[date]
        except KeyError:
            try:
                date = date + BDay(2)
                price = position.prices.loc[date]
            except KeyError:
                price = 0

        return price

    @staticmethod
    def _remove_transactions(transactions, to_remove: list):
        return [trx for trx in transactions if trx.ticker not in to_remove]


if __name__ == '__main__':
    pass
