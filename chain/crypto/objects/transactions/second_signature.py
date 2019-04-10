from .base import BaseTransaction


class SecondSignatureTransaction(BaseTransaction):
    def can_be_applied_to_wallet(self, wallet, wallet_manager, block):
        if wallet.second_public_key:
            print('Wallet already has a second public key')
            return False

        return super().can_be_applied_to_wallet(wallet, wallet_manager, block)

    def apply_to_sender_wallet(self, wallet):
        super().apply_to_sender_wallet(wallet)
        print('APPLYIN SECOND SIGNATURE', self.asset)
        wallet.second_public_key = self.asset["signature"]["publicKey"]

    def revert_for_sender_wallet(self, wallet):
        super().revert_for_sender_wallet(wallet)
        wallet.second_public_key = None

    def can_enter_transaction_pool(self, pool):
        raise NotImplementedError
