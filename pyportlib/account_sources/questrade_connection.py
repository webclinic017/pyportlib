from datetime import datetime
from typing import Union, List
import pandas as pd
import dateutil.parser

import pyportlib.create
from pyportlib.portfolio.iportfolio import IPortfolio
from pyportlib.position.iposition import IPosition
from pyportlib.account_sources.account_source_interface import AccountSourceInterface
from pyportlib.services.interfaces.icash_change import ICashChange
from pyportlib.utils import logger, config_utils
from pyportlib.account_sources.questrade_api.questrade import Questrade
from pyportlib.services.interfaces.itransaction import ITransaction
from pyportlib.utils import dates_utils
from pyportlib import create


class QuestradeConnection(Questrade, AccountSourceInterface):
    def __init__(self, account_name, **kwargs):
        super().__init__(**kwargs)
        self.account_name = account_name.upper()
        self.active_accounts = self.active_accounts()
        self.account_id = self.select_account()

    def select_account(self, select: str = "TFSA"):
        if len(self.active_accounts) == 1:
            return self.active_accounts.get([*self.active_accounts][0])
        else:
            return self.active_accounts.get(select)

    def active_accounts(self):
        accounts = self.accounts.get('accounts')
        active = {}
        for account in accounts:
            if account.get("status") == "Active":
                info = {account.get("type"): account.get("number")}
                active.update(info)

        return active

    def get_positions(self):
        """
        Get positions from the connected account
        :return:
        """
        return self.account_positions(self.account_id)

    def get_balances(self):
        """
        Get balances from the connected account
        :return:
        """
        return self.account_balances(self.account_id)

    def get_transactions(self, start_date: datetime = None, end_date: datetime = None) -> List[dict]:
        """
        Get transactions raw transactions data within a date range from the connected account
        :param start_date: Date to start search
        :param end_date: Date to stop search
        :return: List of dict containing transaction information
        """
        end_date = dates_utils.last_bday(as_of=end_date)

        date_rng = dates_utils.get_market_days(start=start_date, end=end_date)
        list_of_trx = []
        for date in date_rng:
            date = date.isoformat('T') + '-05:00'
            kwargs = {'startTime': date, 'endTime': date}
            trx = self.account_activities(self.account_id, **kwargs).get('activities', self.account_activities(
                self.account_id, **kwargs))
            if trx:
                list_of_trx.extend(trx)

        return list_of_trx

    def _to_cash_changes_list(self, transactions: List[dict]) -> List[ICashChange]:
        """
        Converts list of dicts containing cash change info to a list of CashChange objects
        :param transactions: List of dicts containing cash changes info
        :return: List of CashChange objects
        """
        list_cc = []
        cash_changes = self._filter_cash_changes(transactions)
        for cc in cash_changes:
            cc = self._make_cash_change(cc)
            list_cc.append(cc)

        return list_cc

    def _to_transactions_list(self, transactions: List[dict]) -> List[ITransaction]:
        """
        Converts list of dicts containing transaction info to a list of Transaction objects
        :param transactions: List of dicts containing transaction info
        :return: List of Transaction objects
        """
        list_of_transactions = []
        for i in range(len(transactions)):
            trx = self._make_transaction(transactions[i])
            list_of_transactions.append(trx)

        to_remove = config_utils.fetch_tickers_to_ignore()
        list_of_transactions = self._remove_transactions(
            [pos for pos in list_of_transactions if not isinstance(pos, str) if pos is not None], to_remove)

        return list_of_transactions

    def update_ptf(self, portfolio: IPortfolio, start_date: datetime = None) -> None:
        """
        Updates a pyportlib Portfolio transactions and cash changes and saves the Portfolio. Transactions and Cash Changes will not be duplicated.
        :param portfolio: Portfolio
        :param start_date: Date to start transactions search in connected account
        :return: None
        """
        last_trade = portfolio.transactions.index.max() if not isinstance(portfolio.transactions.index.max(),
                                                                          pd._libs.tslibs.nattype.NaTType) else None
        if not last_trade:
            if start_date:
                last_trade = start_date
            else:
                logger.logging.error(f'no trades, specify start_date for transaction search (questrade_api)')

        transactions = self.get_transactions(start_date=last_trade)
        list_of_cash_changes = self._to_cash_changes_list(transactions)
        list_of_transactions = self._to_transactions_list(transactions)

        list_of_transactions = self._remove_duplicated_transaction(new_transactions=list_of_transactions,
                                                                   ptf_transactions=portfolio.transactions,
                                                                   last_trade_date=last_trade)

        list_of_cash_changes = self._remove_duplicated_cash_change(new_cash_changes=list_of_cash_changes,
                                                                   ptf_cash_changes=portfolio.cash_changes,
                                                                   last_cash_change_date=last_trade)
        portfolio.add_cash_change(list_of_cash_changes)
        portfolio.add_transaction(list_of_transactions)

    def _remove_duplicated_cash_change(self, new_cash_changes: List[ICashChange], ptf_cash_changes: pd.DataFrame,
                                       last_cash_change_date: datetime) -> List[ICashChange]:
        duped = self._duplicated_cash_change(new_cash_changes, ptf_cash_changes, last_cash_change_date)

        cash_changes = []
        for cc in new_cash_changes:
            df = pd.DataFrame([cc.info]).set_index('Date')
            merge = df.merge(duped, indicator=True)
            if merge.empty:
                cash_changes.append(cc)
            else:
                pass

        return cash_changes

    @staticmethod
    def _duplicated_cash_change(new_cash_changes: List[ICashChange], ptf_cash_changes: pd.DataFrame,
                                last_trade_date: datetime) -> pd.DataFrame:
        cash_changes = [cc.info for cc in new_cash_changes]
        try:
            cash_changes = pd.DataFrame(cash_changes).set_index('Date')
            cash_changes = pd.concat([cash_changes, ptf_cash_changes], axis=0).sort_index().loc[last_trade_date:]
        except KeyError:
            cash_changes = pd.DataFrame()
        duped = cash_changes.duplicated()
        return cash_changes.loc[duped]

    def _remove_duplicated_transaction(self, new_transactions: List[ITransaction], ptf_transactions: pd.DataFrame,
                                       last_trade_date: datetime) -> List[ITransaction]:
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
    def _duplicated_transaction(new_transactions: List[ITransaction], ptf_transactions: pd.DataFrame,
                                last_trade_date: datetime) -> pd.DataFrame:
        transactions = pd.concat([trx.df for trx in new_transactions])
        transactions = pd.concat([transactions, ptf_transactions], axis=0).sort_index().loc[last_trade_date:]
        duped = transactions.duplicated()
        return transactions.loc[duped]

    @staticmethod
    def _filter_cash_changes(transactions: list) -> List[dict]:
        return [trx for trx in transactions if trx.get("type") in ["Deposits", "Withdrawals"]]

    @staticmethod
    def _make_cash_change(cash_change: dict) -> ICashChange:
        date = dateutil.parser.isoparse(cash_change.get('tradeDate')).replace(hour=0, minute=0, second=0, microsecond=0,
                                                                              tzinfo=None)
        return pyportlib.create.cash_change(date=date,
                                            direction=cash_change["type"][:-1].title(),
                                            amount=float(cash_change["netAmount"]))

    def _make_transaction(self, transaction) -> Union[ITransaction, None]:
        """
        Makes Transaction object from dict containing transaction info.
        :param transaction:
        :return: Transaction object
        """
        if transaction.get('type') not in ['Trades', 'Dividends', 'Transfers'] or "SPLIT" in transaction.get(
                "description"):
            if transaction.get('type') in ["Deposits", "Withdrawals"]:
                return
            if transaction.get('type').lower() == "other":
                logger.logging.error(f"{transaction.get('type')} not supported")
                return
            logger.logging.error(f"{transaction.get('description')} not supported")
            return

        date = dateutil.parser.isoparse(transaction.get('tradeDate')).replace(hour=0, minute=0, second=0, microsecond=0,
                                                                              tzinfo=None)
        ticker = transaction.get('symbol')
        currency = transaction.get('currency')
        trx_type = transaction.get('type')
        qty = transaction.get('quantity')
        fees = abs(transaction.get('commission'))

        if not isinstance(ticker, float) and ticker:
            pos = create.position(ticker=ticker, local_currency=currency)
        else:
            logger.logging.error(f"{ticker} not supported")
            return

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
                return
            price = self._transfer_cost(position=pos, date=date)
            trx_type = "Buy"

        else:
            logger.logging.error(f"error in transaction {date} {ticker}")
            return

        trx = pyportlib.create.transaction(date=date,
                                           ticker=ticker,
                                           transaction_type=trx_type,
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
                except KeyError:
                    split_factor = 1
                except IndexError:
                    split_factor = 1
            else:
                split_factor = 1
        else:
            split_factor = 1

        return split_factor

    @staticmethod
    def _transfer_cost(position: IPosition, date: datetime) -> float:
        try:
            price = position.prices.loc[date]
        except KeyError:
            try:
                date = date + dates_utils.bday(2)
                price = position.prices.loc[date]
            except KeyError:
                price = 0

        return price

    @staticmethod
    def _remove_transactions(transactions, to_remove: list):
        return [trx for trx in transactions if trx.ticker not in to_remove]


if __name__ == '__main__':
    pass
