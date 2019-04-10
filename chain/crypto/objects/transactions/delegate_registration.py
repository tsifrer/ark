from .base import BaseTransaction


class DelegateRegistrationTransaction(BaseTransaction):
    def can_be_applied_to_wallet(self, wallet, wallet_manager, block):
        username = self.asset["delegate"].get("username")
        if not username:
            print("Delegate username can't be empty")
            return False

        if wallet_manager.delegate_exists(username):
            print(
                "Delegate with the same name ({}) already exists".format(username)
            )
            return False

        return super().can_be_applied_to_wallet(wallet, wallet_manager, block)

    def apply_to_sender_wallet(self, wallet):
        super().apply_to_sender_wallet(wallet)
        wallet.username = self.asset["delegate"]["username"]

    def revert_for_sender_wallet(self, wallet):
        super().revert_for_sender_wallet(wallet)
        wallet.username = None

    def can_enter_transaction_pool(self, pool):
        raise NotImplementedError
