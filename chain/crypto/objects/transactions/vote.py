from .base import BaseTransaction


class VoteTransaction(BaseTransaction):
    def can_be_applied_to_wallet(self, wallet, wallet_manager, block):
        vote = self.asset["votes"][0]
        if vote.startswith("+"):
            if wallet.vote:
                print("Wallet already votes")
                return False
        else:
            if not wallet.vote:
                print("Wallet hasn't voted yet")
                return False
            elif wallet.vote != vote[1:]:
                print("Wallet vote does not match")
                return False

        if not wallet_manager.is_delegate(vote[1:]):
            print("Only delegates can be voted for")
            return False

        return super().can_be_applied_to_wallet(wallet, wallet_manager, block)

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

    def can_enter_transaction_pool(self, pool):
        raise NotImplementedError
