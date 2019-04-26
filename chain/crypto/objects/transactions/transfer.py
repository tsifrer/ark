from chain.plugins.transaction_pool.utils import (
    is_recipient_on_current_network,
)  # TODO: move to different location

from .base import BaseTransaction


class TransferTransaction(BaseTransaction):
    def validate_for_transaction_pool(self, pool, transactions):
        if not is_recipient_on_current_network(self.recipient_id):
            return "Recipient {} is not on the same network".format(self.recipient_id)
        return None
