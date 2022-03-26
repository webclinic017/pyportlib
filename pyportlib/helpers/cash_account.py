from datetime import datetime
from typing import List, Union

import dateutil.parser
import pandas as pd
from ..utils import df_utils, files_utils
from ..utils import logger


class CashAccount:
    NAME = "Cash Account"
    ACCOUNTS_DIRECTORY = files_utils.get_accounts_dir()
    CASH_INFO = ['Date', 'Type', 'Amount']
    CASH_FILENAME = "cash.csv"

    def __init__(self, account):
        self.account = account
        self.directory = f"{self.ACCOUNTS_DIRECTORY}{self.account}"
        self._cash_changes = pd.DataFrame()
        self.load()

    def __repr__(self):
        return self.NAME

    def load(self):
        if files_utils.check_file(self.directory, self.CASH_FILENAME):
            cash = pd.read_csv(f"{self.directory}/{self.CASH_FILENAME}")
            try:
                cash.drop(columns='Unnamed: 0', inplace=True)
            except KeyError:
                pass
            finally:
                if df_utils.check_df_columns(df=cash, columns=self.CASH_INFO):
                    cash.set_index('Date', inplace=True)
                    cash.index.name = 'Date'
                    cash.index = pd.to_datetime(cash.index)
                    self._cash_changes = cash
                else:
                    logger.logging.info(f'cash file does not match requirements: {self.account}')
        else:
            # if new ptf, create required files to use it
            if not files_utils.check_dir(self.directory):
                files_utils.make_dir(self.directory)
            # create empty transaction file in new directory
            empty_cash = self._empty_cash()
            empty_cash.to_csv(f"{self.directory}/{self.CASH_FILENAME}")
            self._cash_changes = empty_cash

    @property
    def cash_changes(self):
        return self._cash_changes

    def get_cash_changes(self):
        return self.cash_changes

    def get_cash_change(self, date):
        c_ch = self.get_cash_changes()
        return c_ch.loc[self.get_cash_changes().index <= date, 'Amount'].sum()

    def _add(self, date: datetime, direction: str, amount: float):
        if direction not in ['deposit', 'withdrawal']:
            raise Exception(f'cash direction type not supported {direction}')

        self.cash_changes.loc[date, "Type"] = direction
        self.cash_changes.loc[date, "Amount"] = amount

        self.cash_changes.to_csv(f"{self.directory}/{self.CASH_FILENAME}")
        self.load()

    def add(self, cash_changes: Union[List[dict], dict]):
        if cash_changes:
            if not hasattr(cash_changes, '__iter__'):
                cash_changes = [cash_changes]

            for cc in cash_changes:
                change = self._clean(cc)
                self._add(date=change["date"], direction=change['direction'], amount=change['amount'])

    def reset(self):
        empty_cash = self._empty_cash()
        empty_cash.to_csv(f"{self.directory}/{self.CASH_FILENAME}")
        self._cash_changes = empty_cash

    def _empty_cash(self):
        return pd.DataFrame(columns=self.CASH_INFO).set_index('Date')

    @staticmethod
    def _clean(cash_change: dict):
        if cash_change.get("tradeDate"):
            assert cash_change["type"] in ["Deposits", "Withdrawals"]
            assert cash_change["netAmount"]

            date = dateutil.parser.isoparse(cash_change.get('tradeDate')).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
            return {"date": date,
                    "direction": cash_change["type"][:-1].lower(),
                    "amount": float(cash_change["netAmount"])}
        else:
            assert isinstance(cash_change.get("date"), datetime)
            assert cash_change["direction"] in ["deposit", "withdrawal"]
            assert isinstance(cash_change["amount"], float)

            return cash_change
