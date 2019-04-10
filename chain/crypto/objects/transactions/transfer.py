from .base import BaseTransaction


class TransferTransaction(BaseTransaction):

    def can_enter_transaction_pool(self, pool):
        raise NotImplementedError
