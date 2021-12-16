import pandas as pd

from utils import files_utils, df_utils
from utils.logger import logger


class CashAccount:
    NAME = "Cash Account"
    ACCOUNTS_DIRECTORY = "client_data/accounts/"
    CASH_INFO = ['Date', 'Type', 'Amount']

    def __init__(self, account):
        self.account = account
        self.directory = f"{self.ACCOUNTS_DIRECTORY}{self.account}"
        self.filename = f"{self.account}_cash.csv"
        self.cash_changes = self._load_cash()
        self.cash_series = pd.Series()

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
            empty_cash = pd.DataFrame(columns=self.CASH_INFO).set_index('Date')
            empty_cash.to_csv(f"{self.directory}/{self.filename}")
            return empty_cash

    def get_cash_changes(self):
        return self.cash_changes

    def get_cash_change(self, date):
        return self.get_cash_changes().loc[self.get_cash_changes().index <= date, 'Amount'].sum()
