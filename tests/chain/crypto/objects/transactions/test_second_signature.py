from chain.crypto.constants import TRANSACTION_TYPE_SECOND_SIGNATURE
from chain.crypto.models.wallet import Wallet
from chain.crypto.objects.transactions.second_signature import (
    SecondSignatureTransaction,
)


def test_can_be_applied_to_wallet_returns_false_if_username_is_not_set():
    transaction = SecondSignatureTransaction()
    wallet = Wallet({"second_public_key": "harambe"})
    can_apply = transaction.can_be_applied_to_wallet(wallet, None, None)
    assert can_apply is False


def test_can_be_applied_to_wallet_calls_super(mocker):
    transaction = SecondSignatureTransaction()
    wallet = Wallet({})
    super_mock = mocker.patch(
        (
            "chain.crypto.objects.transactions.second_signature.BaseTransaction."
            "can_be_applied_to_wallet"
        ),
        return_value=True,
    )
    can_apply = transaction.can_be_applied_to_wallet(wallet, None, None)
    assert can_apply is True
    assert super_mock.call_count == 1


def test_appply_to_sender_wallet(mocker):
    transaction = SecondSignatureTransaction()
    transaction.asset = {"signature": {"publicKey": "harambe"}}
    wallet = Wallet({})

    super_mock = mocker.patch(
        "chain.crypto.objects.transactions.delegate_registration.BaseTransaction."
        "apply_to_sender_wallet"
    )

    transaction.apply_to_sender_wallet(wallet)
    assert super_mock.call_count == 1
    assert wallet.second_public_key == "harambe"


def test_revert_for_sender_wallet(mocker):
    transaction = SecondSignatureTransaction()
    transaction.asset = {"signature": {"publicKey": "harambe"}}
    wallet = Wallet({"second_public_key": "harambe"})

    super_mock = mocker.patch(
        "chain.crypto.objects.transactions.delegate_registration.BaseTransaction."
        "revert_for_sender_wallet"
    )

    transaction.revert_for_sender_wallet(wallet)
    assert super_mock.call_count == 1
    assert wallet.second_public_key is None


def test_validate_for_transaction_pool_returns_error_for_existing_type(mocker):
    transaction = SecondSignatureTransaction()
    transaction.sender_public_key = (
        "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
    )
    transaction.type = TRANSACTION_TYPE_SECOND_SIGNATURE

    pool = mocker.Mock()
    pool.sender_has_transactions_of_type = lambda x: True

    response = transaction.validate_for_transaction_pool(pool, None)
    assert response == (
        "Sender 020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325 "
        "already has a transaction of type 1 in the pool"
    )


def test_validate_for_transaction_pool(mocker):
    transaction = SecondSignatureTransaction()
    transaction.sender_public_key = (
        "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
    )
    transaction.type = TRANSACTION_TYPE_SECOND_SIGNATURE

    pool = mocker.Mock()
    pool.sender_has_transactions_of_type = lambda x: False
    response = transaction.validate_for_transaction_pool(pool, [transaction])
    assert response is None
