from datetime import datetime
from typing import Union, List
import pandas as pd
from pandas._libs.tslibs.offsets import BDay
from ..utils import logger
from .questrade_api.questrade import Questrade
import dateutil.parser
from ..helpers.transaction import Transaction
from ..portfolio import Portfolio
from ..position import Position
from ..utils import dates_utils


class QuestradeConnection(Questrade):
    def __init__(self, account_name, **kwargs):
        super().__init__(**kwargs)
        self.account_name = account_name.upper()

    def _get_account_id(self):
        accounts = self.accounts.get('accounts')
        tfsa_id = [acc for acc in accounts if acc.get('type') == self.account_name and acc.get('status') == 'Active'][
            0].get('number')
        return tfsa_id

    def get_positions(self):
        return self.account_positions(self._get_account_id())

    def get_balances(self):
        return self.account_balances(self._get_account_id())

    def get_transactions(self, start_date: datetime = None, end_date: datetime = None) -> List[dict]:

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

    def to_cash_changes_list(self, transactions: List[dict]):
        list_cc = []
        cash_changes = self._filter_cash_changes(transactions)
        for cc in cash_changes:
            cc = self._make_cash_change(cc)
            list_cc.append(cc)

        return list_cc

    def to_transactions_list(self, transactions: List[dict]) -> List[Transaction]:
        list_of_transactions = []
        for i in range(len(transactions)):
            trx = self._make_transaction(transactions[i])
            list_of_transactions.append(trx)

        to_remove = ['ARRY', "IPL.TO"]
        list_of_transactions = self._remove_transactions(
            [pos for pos in list_of_transactions if not isinstance(pos, str)], to_remove)

        return list_of_transactions

    def update_transactions(self, portfolio: Portfolio, start_date: datetime = None) -> None:
        last_trade = portfolio.transactions.index.max() if not isinstance(portfolio.transactions.index.max(),
                                                                          pd._libs.tslibs.nattype.NaTType) else None
        if not last_trade:
            if start_date:
                last_trade = start_date
            else:
                logger.logging.error(f'no trades, specify start_date for transaction search (questrade_api)')

        transactions = self.get_transactions(start_date=last_trade)
        list_of_cash_changes = self.to_cash_changes_list(transactions)
        list_of_transactions = self.to_transactions_list(transactions)

        list_of_transactions = self._remove_duplicated_transaction(new_transactions=list_of_transactions,
                                                                   ptf_transactions=portfolio.transactions,
                                                                   last_trade_date=last_trade)

        list_of_cash_changes = self._remove_duplicated_cash_change(new_cash_changes=list_of_cash_changes,
                                                                   ptf_cash_changes=portfolio.cash_changes,
                                                                   last_cash_change_date=last_trade)
        portfolio.add_cash_change(list_of_cash_changes)
        portfolio.add_transaction(list_of_transactions)

    def _remove_duplicated_cash_change(self, new_cash_changes: List[dict], ptf_cash_changes: pd.DataFrame,
                                       last_cash_change_date: datetime) -> List[dict]:

        duped = self._duplicated_cash_change(new_cash_changes, ptf_cash_changes, last_cash_change_date)

        cash_changes = []
        for cc in new_cash_changes:
            df = pd.DataFrame([cc]).set_index('Date')
            merge = df.merge(duped, indicator=True)
            if merge.empty:
                cash_changes.append(cc)
            else:
                pass

        return cash_changes

    @staticmethod
    def _duplicated_cash_change(new_cash_changes: List[dict], ptf_cash_changes: pd.DataFrame,
                                last_trade_date: datetime):

        cash_changes = pd.DataFrame(new_cash_changes).set_index('Date')
        cash_changes = pd.concat([cash_changes, ptf_cash_changes], axis=0).sort_index().loc[last_trade_date:]

        duped = cash_changes.duplicated()
        return cash_changes.loc[duped]

    def _remove_duplicated_transaction(self, new_transactions: List[Transaction], ptf_transactions: pd.DataFrame,
                                       last_trade_date: datetime):
        duped = self._duplicated_transaction(new_transactions=new_transactions, ptf_transactions=ptf_transactions,
                                             last_trade_date=last_trade_date)
        transactions = []
        for trx in new_transactions:
            merge = trx.df.merge(duped, indicator=True)
            if merge.empty:
                transactions.append(trx)
            else:
                pass

        return transactions

    @staticmethod
    def _duplicated_transaction(new_transactions: List[Transaction], ptf_transactions: pd.DataFrame,
                                last_trade_date: datetime):
        transactions = pd.concat([trx.df for trx in new_transactions])
        transactions = pd.concat([transactions, ptf_transactions], axis=0).sort_index().loc[last_trade_date:]
        duped = transactions.duplicated()
        return transactions.loc[duped]

    @staticmethod
    def _filter_cash_changes(transactions: list):
        return [trx for trx in transactions if trx.get("type") in ["Deposits", "Withdrawals"]]

    @staticmethod
    def _make_cash_change(cash_change: dict):
        date = dateutil.parser.isoparse(cash_change.get('tradeDate')).replace(hour=0, minute=0, second=0, microsecond=0,
                                                                              tzinfo=None)
        return {"Date": date,
                "Direction": cash_change["type"][:-1].title(),
                "Amount": float(cash_change["netAmount"])}

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

        if not isinstance(ticker, float) and ticker:
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
            trx_type = "Buy"

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
