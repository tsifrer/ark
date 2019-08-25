import logging

from .base import BaseTransaction

logger = logging.getLogger(__name__)


class SecondSignatureTransaction(BaseTransaction):
    def can_be_applied_to_wallet(self, wallet, wallet_manager, block_height):
        if wallet.second_public_key:
            logger.warning("Wallet already has a second public key")
            return False

        return super().can_be_applied_to_wallet(wallet, wallet_manager, block_height)

    def apply_to_sender_wallet(self, wallet):
        super().apply_to_sender_wallet(wallet)
        wallet.second_public_key = self.asset["signature"]["publicKey"]

    def revert_for_sender_wallet(self, wallet):
        super().revert_for_sender_wallet(wallet)
        wallet.second_public_key = None

    def validate_for_transaction_pool(self, pool, transactions):
        if pool.sender_has_transactions_of_type(self):
            return (
                "Sender {} already has a transaction of type {} in the "
                "pool".format(self.sender_public_key, self.type)
            )
        return None
