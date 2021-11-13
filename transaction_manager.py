from transaction import Transaction
from utils.df_utils import check_csv
from utils.files_utils import check_file, check_dir, make_dir
import pandas as pd


class TransactionManager(object):
    name = "Transactions Manager"
    ACCOUNTS_DIRECTORY = "client_data/accounts/"

    def __init__(self, account):
        self.account = account
        self.directory = f"{self.ACCOUNTS_DIRECTORY}{self.account}"
        self.filename = f"{self.account}_transactions.csv"
        self.transactions = self.fetch()

    def __repr__(self):
        return self.name

    def fetch(self) -> pd.DataFrame:
        if check_file(self.directory, self.filename):
            trx = pd.read_csv(f"{self.directory}/{self.filename}")
            try:
                trx.drop(columns='Unnamed: 0', inplace=True)
            except KeyError:
                pass
            finally:
                if check_csv(trx, Transaction.TRANSACTIONS_INFO):
                    trx.set_index('Date', inplace=True)
                    trx.index.NAME = 'Date'
                    return trx
                else:
                    raise KeyError("transactions csv file has wrong format")
        else:
            # transactions do not exist check if portfolio directory exists
            if not check_dir(self.directory):
                make_dir(self.directory)
            # create empty transaction file
            empty_transactions = pd.DataFrame(columns=Transaction.TRANSACTIONS_INFO).set_index('Date')
            empty_transactions.to_csv(f"{self.directory}/{self.filename}")
            return empty_transactions

    def write(self) -> None:
        self.transactions.index.name = 'Date'
        self.transactions.to_csv(f"{self.directory}/{self.filename}")
        print('transactions file updated')

    def add(self, transaction: Transaction) -> None:
        new = transaction.get()
        self.transactions = pd.concat([self.transactions, new])

        new_qty = self.transactions.Quantity.loc[self.transactions.Ticker == transaction.ticker].sum()
        excess = -1 * (transaction.quantity - (transaction.quantity - new_qty))
        if new_qty < 0:
            raise ValueError(f'no short positions allowed, you sold {excess} units too many')

        self.write()
        print(f'{transaction} added to account: {self.account}')

    def all_tickers(self) -> list:
        tickers = list(set(self.transactions.Ticker))
        return tickers

    def live_tickers(self) -> list:
        live_tickers = self.transactions.groupby('Ticker').sum()
        live_tickers = live_tickers.loc[live_tickers.Quantity > 0]
        return list(live_tickers.index)

    def total_fees(self) -> float:
        return self.transactions.Fees.sum()
