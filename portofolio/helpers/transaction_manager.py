from typing import List
from ..helpers.transaction import Transaction
from ..utils import logger, df_utils, files_utils
import pandas as pd


class TransactionManager(object):
    NAME = "Transactions Manager"
    ACCOUNTS_DIRECTORY = files_utils.get_accounts_dir()
    TRANSACTION_FILENAME = "transactions.csv"

    def __init__(self, account):
        self.account = account
        self.directory = f"{self.ACCOUNTS_DIRECTORY}{self.account}"
        self.transactions = pd.DataFrame()
        self.fetch()

    def __repr__(self):
        return self.NAME

    def fetch(self) -> pd.DataFrame:
        if files_utils.check_file(self.directory, self.TRANSACTION_FILENAME):
            trx = pd.read_csv(f"{self.directory}/{self.TRANSACTION_FILENAME}")
            try:
                trx.drop(columns='Unnamed: 0', inplace=True)
            except KeyError:
                pass
            finally:
                if df_utils.check_df_columns(df=trx, columns=Transaction.TRANSACTIONS_INFO):
                    trx.set_index('Date', inplace=True)
                    trx.index.name = 'Date'
                    trx.index = pd.to_datetime(trx.index)
                    self.transactions = trx
                    return trx
                else:
                    logger.logging.error(f'transactions do not match requirements for account: {self.account}')
        else:
            # if new ptf, create required files to use it
            if not files_utils.check_dir(self.directory):
                files_utils.make_dir(self.directory)
            # create empty transaction file in new directory
            empty_transactions = self.empty_transactions()
            empty_transactions.to_csv(f"{self.directory}/{self.TRANSACTION_FILENAME}")
            self.transactions = empty_transactions
            return empty_transactions

    def _write_trx(self, transaction: Transaction) -> None:
        new = transaction.get()
        self.transactions = pd.concat([self.transactions, new])

        self.transactions.to_csv(f"{self.directory}/{self.TRANSACTION_FILENAME}")
        logger.logging.debug('transactions file updated')

    def _check_trx(self, transaction: Transaction) -> bool:
        new_qty = self.transactions.Quantity.loc[self.transactions.Ticker == transaction.ticker].sum() + transaction.quantity

        if new_qty < 0:
            print(transaction.get())
            logger.logging.error(f'no short positions allowed, you sold {-1 * (transaction.quantity - (transaction.quantity - new_qty))} units too many')
            return False
        else:
            return True

    def add(self, transaction: Transaction) -> None:
        if self._check_trx(transaction):
            self._write_trx(transaction)
            logger.logging.info(f'{transaction} was added to account: {self.account}')

    def all_positions(self) -> list:
        try:
            tickers = list(set(self.transactions.Ticker))
            return tickers
        except AttributeError:
            logger.logging.error(f'no tickers found for account: {self.account}')
            return []

    def live_positions(self) -> list:
        live_tickers = self.transactions.groupby('Ticker').sum()
        try:
            live_tickers = live_tickers.loc[live_tickers.Quantity > 0]
            return list(live_tickers.index)
        except AttributeError:
            logger.logging.error(f'no tickers found for account: {self.account}')
            return []

    def total_fees(self) -> float:
        return self.transactions.Fees.sum()
    
    def first_trx(self, ticker: str = None):
        if len(self.get_transactions()):
            if ticker:
                return self.transactions.loc[self.transactions.Ticker == ticker].index.min()
            return self.get_transactions().index.min()
        else:
            return None

    def last_trx(self, ticker: str = None):
        if len(self.get_transactions()):
            if ticker:
                return self.transactions.loc[self.transactions.Ticker == ticker].index.max()
            return self.get_transactions().index.max()
        else:
            return None

    def get_currencies(self):
        currencies = set(self.transactions.Currency)
        return currencies

    def get_currency(self, ticker: str):
        return self.get_transactions().loc[self.get_transactions()['Ticker'] == ticker, 'Currency'].iloc[0]

    def get_transactions(self):
        return self.transactions

    def from_csv(self, filename) -> List[Transaction]:
        raise NotImplementedError()

    def reset(self):
        empty_transactions = self.empty_transactions()
        empty_transactions.to_csv(f"{self.directory}/{self.TRANSACTION_FILENAME}")
        self.transactions = empty_transactions

    @staticmethod
    def empty_transactions():
        return pd.DataFrame(columns=Transaction.TRANSACTIONS_INFO).set_index('Date')
