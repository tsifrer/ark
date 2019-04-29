from chain.plugins.transaction_pool.utils import (
    is_recipient_on_current_network,
)  # TODO: move to different location

from .base import BaseTransaction


class TransferTransaction(BaseTransaction):
    def validate_for_transaction_pool(self, pool, transactions):
        if not is_recipient_on_current_network(self.recipient_id):
            return "Recipient {} is not on the same network".format(self.recipient_id)
        return None

    def apply(self, sender, recipient, wallet_manager):
        """Apply transaction to recipient wallet

        :param (Wallet) sender: sender Wallet object
        :param (Wallet) recipient: recipient Wallet object or None if recipient is not
                                   set
        :param (WalletManager) wallet_manager: Wallet manager object
        """
        if recipient:
            self.apply_to_recipient_wallet(recipient)
            wallet_manager.save_wallet(recipient)
