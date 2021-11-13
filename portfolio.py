from transaction_manager import TransactionManager


class Portfolio(object):

    def __init__(self,
                 account: str):

        self.account = account
        self.transaction_service = TransactionManager(account=self.account)

    def __repr__(self):
        return self.account

