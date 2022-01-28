from datetime import datetime

import pandas as pd

from portofolio.utils import df_utils, files_utils
from portofolio.utils.logger import logger


class CashAccount:
    NAME = "Cash Account"
    ACCOUNTS_DIRECTORY = "client_data/accounts/"
    CASH_INFO = ['Date', 'Type', 'Amount']

    def __init__(self, account):
        self.account = account
        self.directory = f"{self.ACCOUNTS_DIRECTORY}{self.account}"
        self.filename = f"{self.account}_cash.csv"
        self.cash_changes = self._load_cash()

    def __repr__(self):
        return self.NAME

    def _load_cash(self):
        if files_utils.check_file(self.directory, self.filename):
            cash = pd.read_csv(f"{self.directory}/{self.filename}")
            try:
                cash.drop(columns='Unnamed: 0', inplace=True)
            except KeyError:
                pass
            finally:
                if df_utils.check_df_columns(df=cash, columns=self.CASH_INFO):
                    cash.set_index('Date', inplace=True)
                    cash.index.name = 'Date'
                    cash.index = pd.to_datetime(cash.index)
                    return cash
                else:
                    logger.logging.info(f'cash file does not match requirements: {self.account}')
        else:
            # if new ptf, create required files to use it
            if not files_utils.check_dir(self.directory):
                files_utils.make_dir(self.directory)
            # create empty transaction file in new directory
            empty_cash = self.empty_cash()
            empty_cash.to_csv(f"{self.directory}/{self.filename}")
            return empty_cash

    def get_cash_changes(self):
        return self.cash_changes

    def get_cash_change(self, date):
        c_ch = self.get_cash_changes()
        return c_ch.loc[self.get_cash_changes().index <= date, 'Amount'].sum()

    def add_cash_change(self, date: datetime, direction: str, amount: float):
        if direction not in ['Deposit', 'Withdrawal']:
            raise Exception(f'cash direction type not supported {direction}')

        self.cash_changes.loc[date, "Type"] = direction
        self.cash_changes.loc[date, "Amount"] = amount

        self.cash_changes.to_csv(f"{self.directory}/{self.filename}")
        self._load_cash()

    def reset_cash(self):
        empty_cash = self.empty_cash()
        empty_cash.to_csv(f"{self.directory}/{self.filename}")
        self.cash_changes = empty_cash

    def empty_cash(self):
        return pd.DataFrame(columns=self.CASH_INFO).set_index('Date')
