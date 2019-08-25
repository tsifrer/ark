import logging

from .base import BaseTransaction

logger = logging.getLogger(__name__)


class VoteTransaction(BaseTransaction):
    def can_be_applied_to_wallet(self, wallet, wallet_manager, block_height):
        vote = self.asset["votes"][0]
        if vote.startswith("+"):
            if wallet.vote:
                logger.warning("Wallet already votes")
                return False
        else:
            if not wallet.vote:
                logger.error("Wallet hasn't voted yet")
                return False
            elif wallet.vote != vote[1:]:
                logger.error("Wallet vote doesn't match")
                return False

        if not wallet_manager.is_delegate(vote[1:]):
            logger.error("Only delegates can be voted for")
            return False

        return super().can_be_applied_to_wallet(wallet, wallet_manager, block_height)

    def apply_to_sender_wallet(self, wallet):
        super().apply_to_sender_wallet(wallet)
        vote = self.asset["votes"][0]
        if vote.startswith("+"):
            wallet.vote = vote[1:]
        else:
            wallet.vote = None

    def revert_for_sender_wallet(self, wallet):
        super().revert_for_sender_wallet(wallet)
        vote = self.asset["votes"][0]
        if vote.startswith("+"):
            wallet.vote = None
        else:
            wallet.vote = vote[1:]

    def validate_for_transaction_pool(self, pool, transactions):
        if pool.sender_has_transactions_of_type(self):
            return (
                "Sender {} already has a transaction of type {} in the "
                "pool".format(self.sender_public_key, self.type)
            )
        return None
