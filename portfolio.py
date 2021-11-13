from transaction_manager import TransactionManager


class Portfolio(object):

    def __init__(self, account: str):

        self.account = account
        self.transaction_manager = TransactionManager(account=self.account)
        self.positions = {}

    def __repr__(self):
        return self.account

    def get_position(self, ticker):
        return self.positions.get(ticker)


