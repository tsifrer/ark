from chain.crypto.constants import TRANSACTION_TYPE_VOTE
from chain.crypto.models.wallet import Wallet
from chain.crypto.objects.transactions.vote import VoteTransaction


def test_can_be_applied_to_wallet_returns_false_if_wallet_already_votes():
    transaction = VoteTransaction()
    transaction.asset = {"votes": ["+harambe"]}
    wallet = Wallet({"vote": "harambe"})
    can_apply = transaction.can_be_applied_to_wallet(wallet, None, None)
    assert can_apply is False


def test_can_be_applied_to_wallet_returns_false_if_wallet_does_not_vote():
    transaction = VoteTransaction()
    transaction.asset = {"votes": ["-harambe"]}
    wallet = Wallet({})
    can_apply = transaction.can_be_applied_to_wallet(wallet, None, None)
    assert can_apply is False


def test_can_be_applied_to_wallet_returns_false_if_votes_do_not_match():
    transaction = VoteTransaction()
    transaction.asset = {"votes": ["-harambe"]}
    wallet = Wallet({"vote": "spongebob"})
    can_apply = transaction.can_be_applied_to_wallet(wallet, None, None)
    assert can_apply is False


def test_can_be_applied_to_wallet_returns_false_if_delegate_does_not_exist(mocker):
    transaction = VoteTransaction()
    transaction.asset = {"votes": ["+harambe"]}
    wallet = Wallet({})
    manager = mocker.Mock()
    manager.is_delegate = lambda x: False
    can_apply = transaction.can_be_applied_to_wallet(wallet, manager, None)
    assert can_apply is False


def test_can_be_applied_to_wallet_calls_super_for_vote(mocker):
    transaction = VoteTransaction()
    transaction.asset = {"votes": ["+harambe"]}
    wallet = Wallet({})
    super_mock = mocker.patch(
        (
            "chain.crypto.objects.transactions.vote.BaseTransaction."
            "can_be_applied_to_wallet"
        ),
        return_value=True,
    )
    manager = mocker.Mock()
    manager.is_delegate = lambda x: True
    can_apply = transaction.can_be_applied_to_wallet(wallet, manager, None)
    assert can_apply is True
    assert super_mock.call_count == 1


def test_can_be_applied_to_wallet_calls_super_for_unvote(mocker):
    transaction = VoteTransaction()
    transaction.asset = {"votes": ["-harambe"]}
    wallet = Wallet({"vote": "harambe"})
    super_mock = mocker.patch(
        (
            "chain.crypto.objects.transactions.vote.BaseTransaction."
            "can_be_applied_to_wallet"
        ),
        return_value=True,
    )
    manager = mocker.Mock()
    manager.is_delegate = lambda x: True
    can_apply = transaction.can_be_applied_to_wallet(wallet, manager, None)
    assert can_apply is True
    assert super_mock.call_count == 1


def test_appply_to_sender_wallet_for_vote(mocker):
    transaction = VoteTransaction()
    transaction.asset = {"votes": ["+harambe"]}
    wallet = Wallet({})
    super_mock = mocker.patch(
        "chain.crypto.objects.transactions.vote.BaseTransaction."
        "apply_to_sender_wallet"
    )

    transaction.apply_to_sender_wallet(wallet)
    assert super_mock.call_count == 1
    assert wallet.vote == "harambe"


def test_appply_to_sender_wallet_for_unvote(mocker):
    transaction = VoteTransaction()
    transaction.asset = {"votes": ["-harambe"]}
    wallet = Wallet({"vote": "harambe"})
    super_mock = mocker.patch(
        "chain.crypto.objects.transactions.vote.BaseTransaction."
        "apply_to_sender_wallet"
    )

    transaction.apply_to_sender_wallet(wallet)
    assert super_mock.call_count == 1
    assert wallet.vote is None


def test_revert_for_sender_wallet_for_vote(mocker):
    transaction = VoteTransaction()
    transaction.asset = {"votes": ["+harambe"]}
    wallet = Wallet({})
    super_mock = mocker.patch(
        "chain.crypto.objects.transactions.vote.BaseTransaction."
        "revert_for_sender_wallet"
    )
    transaction.revert_for_sender_wallet(wallet)
    assert super_mock.call_count == 1
    assert wallet.username is None


def test_revert_to_sender_wallet_for_unvote(mocker):
    transaction = VoteTransaction()
    transaction.asset = {"votes": ["-harambe"]}
    wallet = Wallet({"vote": "harambe"})
    super_mock = mocker.patch(
        "chain.crypto.objects.transactions.vote.BaseTransaction."
        "revert_for_sender_wallet"
    )

    transaction.revert_for_sender_wallet(wallet)
    assert super_mock.call_count == 1
    assert wallet.vote == "harambe"


def test_validate_for_transaction_pool_returns_error_for_existing_type(mocker):
    transaction = VoteTransaction()
    transaction.sender_public_key = (
        "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
    )
    transaction.type = TRANSACTION_TYPE_VOTE

    pool = mocker.Mock()
    pool.sender_has_transactions_of_type = lambda x: True

    response = transaction.validate_for_transaction_pool(pool, None)
    assert response == (
        "Sender 020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325 "
        "already has a transaction of type 3 in the pool"
    )
