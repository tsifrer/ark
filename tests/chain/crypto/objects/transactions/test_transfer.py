import json

from chain.crypto.models.wallet import Wallet
from chain.crypto.objects.transactions.transfer import TransferTransaction
from chain.plugins.database.wallet_manager import WalletManager


def test_apply(redis, mocker):
    transaction = TransferTransaction()
    transaction.recipient_id = "DB4gFuDztmdGALMb8i1U4Z4R5SktxpNTAY"
    manager = WalletManager()
    recipient = Wallet({"address": "AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof"})
    apply_mock = mocker.patch.object(transaction, "apply_to_recipient_wallet")

    transaction.apply(None, recipient, manager)

    data = json.loads(redis.get("wallets:address:AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof"))
    assert data["address"] == recipient.address
    assert apply_mock.call_count == 1


def test_validate_for_transaction_pool_returns_error_for_wrong_recipient():
    transaction = TransferTransaction()
    transaction.recipient_id = "DB4gFuDztmdGALMb8i1U4Z4R5SktxpNTAY"
    response = transaction.validate_for_transaction_pool(None, None)
    assert response == (
        "Recipient DB4gFuDztmdGALMb8i1U4Z4R5SktxpNTAY is not on the same network"
    )


def test_validate_for_transaction_pool():
    transaction = TransferTransaction()
    transaction.recipient_id = "AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof"
    response = transaction.validate_for_transaction_pool(None, None)
    assert response is None
