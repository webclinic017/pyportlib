import pandas as pd

from ..services.transaction import Transaction
from ..utils import logger, df_utils, files_utils


class TransactionManager:
    NAME = "Transactions Manager"
    _ACCOUNTS_DIRECTORY = files_utils.get_accounts_dir()
    _TRANSACTION_FILENAME = "transactions.csv"

    def __init__(self, account):
        self.account = account
        self.directory = f"{self._ACCOUNTS_DIRECTORY}{self.account}"
        self._transactions = pd.DataFrame()
        self.load()

    def __repr__(self):
        return self.NAME

    @property
    def transactions(self):
        return self._transactions

    def load(self) -> None:
        if files_utils.check_file(self.directory, self._TRANSACTION_FILENAME):
            trx = pd.read_csv(f"{self.directory}/{self._TRANSACTION_FILENAME}")
            try:
                trx.drop(columns='Unnamed: 0', inplace=True)
            except KeyError:
                pass
            finally:
                if df_utils.check_df_columns(df=trx, columns=Transaction.INFO):
                    trx.set_index('Date', inplace=True)
                    trx.index.name = 'Date'
                    trx.index = pd.to_datetime(trx.index)
                    self._transactions = trx

                else:
                    logger.logging.error(f'transactions do not match requirements for account: {self.account}')
        else:
            # if new ptf, create required files to use it
            if not files_utils.check_dir(self.directory):
                files_utils.make_dir(self.directory)
            # create empty transaction file in new directory
            empty_transactions = self.empty_transactions()
            empty_transactions.to_csv(f"{self.directory}/{self._TRANSACTION_FILENAME}")
            self._transactions = empty_transactions

    def _write_trx(self, transaction: Transaction) -> None:
        new = transaction.df
        self._transactions = pd.concat([self._transactions, new])

        self._transactions.to_csv(f"{self.directory}/{self._TRANSACTION_FILENAME}")
        logger.logging.debug('transactions file updated')

    def _save_trx_df(self) -> None:
        self._transactions.to_csv(f"{self.directory}/{self._TRANSACTION_FILENAME}")
        logger.logging.debug('transactions file updated')

    @staticmethod
    def _check_trx(transaction: Transaction) -> bool:
        assert transaction
        return True

    def add(self, transaction: Transaction) -> None:
        if self._check_trx(transaction):
            self._write_trx(transaction)

            logger.logging.debug(f'{transaction} was added to account: {self.account}')

    def all_tickers(self) -> list:
        try:
            tickers = list(set(self._transactions.Ticker))
            return tickers
        except AttributeError:
            logger.logging.error(f'no tickers found for account: {self.account}')
            return []

    def total_fees(self) -> float:
        return self._transactions.Fees.sum()
    
    def first_transaction(self, ticker: str = None):
        if len(self._transactions):
            if ticker:
                return self._transactions.loc[self._transactions.Ticker == ticker].index.min()
            return self._transactions.index.min()
        else:
            return None

    def last_transaction(self, ticker: str = None):
        if len(self._transactions):
            if ticker:
                return self._transactions.loc[self._transactions.Ticker == ticker].index.max()
            return self._transactions.index.max()
        else:
            return None

    def get_currencies(self) -> set:
        currencies = set(self._transactions.Currency)
        return currencies

    def get_currency(self, ticker: str) -> str:
        return self._transactions.loc[self._transactions['Ticker'] == ticker, 'Currency'].iloc[0]

    def reset(self):
        empty_transactions = self.empty_transactions()
        empty_transactions.to_csv(f"{self.directory}/{self._TRANSACTION_FILENAME}")
        self._transactions = empty_transactions

    def add_split(self, transaction: Transaction):
        """
        Creates a split and corrects historic ticker transactions for that split
        :param transaction: split transaction
        :return:
        """
        self.add(transaction)

        self._transactions.loc[(self._transactions['Ticker'] == transaction.ticker) & (self._transactions['Type'].isin(["Buy", "Sell"])), 'Price'] /= transaction.price
        self._transactions.loc[(self._transactions['Ticker'] == transaction.ticker) & (self._transactions['Type'].isin(["Buy", "Sell"])), 'Quantity'] *= transaction.price
        self._save_trx_df()

    @staticmethod
    def empty_transactions():
        return pd.DataFrame(columns=Transaction.INFO).set_index('Date')
