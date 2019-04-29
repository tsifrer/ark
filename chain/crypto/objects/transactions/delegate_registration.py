from chain.crypto.constants import TRANSACTION_TYPE_DELEGATE_REGISTRATION
from chain.plugins.database.models.pool_transaction import PoolTransaction

from .base import BaseTransaction


class DelegateRegistrationTransaction(BaseTransaction):
    def can_be_applied_to_wallet(self, wallet, wallet_manager, block_height):
        username = self.asset["delegate"].get("username")
        if not username:
            print("Delegate username can't be empty")
            return False

        if wallet_manager.delegate_exists(username):
            print("Delegate with the same name ({}) already exists".format(username))
            return False

        return super().can_be_applied_to_wallet(wallet, wallet_manager, block_height)

    def apply_to_sender_wallet(self, wallet):
        super().apply_to_sender_wallet(wallet)
        wallet.username = self.asset["delegate"]["username"]

    def revert_for_sender_wallet(self, wallet):
        super().revert_for_sender_wallet(wallet)
        wallet.username = None

    def validate_for_transaction_pool(self, pool, transactions):
        if self.sender_has_transactions_of_type(self):
            return (
                "Sender {} already has a transaction of type {} in the "
                "pool".format(self.sender_public_key, self.type)
            )

        # Reject all delegate registration transactions with the same delegate
        # name if there are more than one with the same name
        num_same_delegate_registration_in_payload = [
            trans
            for trans in transactions
            if trans.asset["delegate"]["username"] == self.asset["delegate"]["username"]
        ]
        if len(num_same_delegate_registration_in_payload) > 1:
            return (
                "Multiple delegate registrations for {} in transaction "
                "payload".format(self.asset["delegate"]["username"])
            )

        # Reject a transaction if delegate registration transaction for the same
        # username is already in the pool
        exists_in_pool = (
            PoolTransaction.select()
            .where(
                PoolTransaction.type == TRANSACTION_TYPE_DELEGATE_REGISTRATION,
                PoolTransaction.asset["delegate"]["username"]
                == self.asset["delegate"]["username"],
            )
            .exists()
        )
        if exists_in_pool:
            return "Delegate registration for {} already in the pool".format(
                self.asset["delegate"]["username"]
            )

        return None

    def apply(self, sender, recipient, wallet_manager):
        """Add sender wallet to the _username_map

        :param (Wallet) sender: sender Wallet object
        :param (Wallet) recipient: recipient Wallet object or None if recipient is not
                                   set
        :param (WalletManager) wallet_manager: Wallet manager object
        """
        print("Registering delegate")
        wallet_manager.redis.set(
            wallet_manager.key_for_username(sender.username), sender.address
        )
