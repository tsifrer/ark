import os

import pytest

from redis import Redis

from chain.common.config import config
from chain.crypto.objects.block import Block as CryptoBlock
from chain.p2p_service.server import create_app
from chain.plugins.database.database import Database
from chain.plugins.database.migrate import migrate
from chain.plugins.database.models.block import Block
from chain.plugins.database.models.round import Round
from chain.plugins.database.models.transaction import Transaction

from tests.chain.fixtures import (  # noqa
    dummy_block_full_hash,
    dummy_block_hash,
    dummy_transaction_hash,
    dummy_transaction,
    dummy_block,
    crypto_transaction,
    crypto_block,
)


def _clear_db():
    Round.delete().execute()
    Transaction.delete().execute()
    Block.delete().execute()

def _create_genesis_block():
    _clear_db()
    block = CryptoBlock.from_dict(config.genesis_block)

    db_block = Block.from_crypto(block)
    db_block.save(force_insert=True)

    for transaction in block.transactions:
        db_trans = Transaction.from_crypto(transaction)
        db_trans.save(force_insert=True)

    # BlockFactory(
    #     id=genesis_block['id'],
    #     version=genesis_block['version'],
    #     timestamp=genesis_block['timestamp'],
    #     previous_block=genesis_block['previousBlock'],
    #     height=genesis_block['height'],
    #     number_of_transactions=genesis_block['numberOfTransactions'],
    #     total_amount=genesis_block['totalAmount'],
    #     total_fee=genesis_block['totalFee'],
    #     reward=genesis_block['reward'],
    #     payload_length=genesis_block['payloadLength'],
    #     payload_hash=genesis_block['payloadHash'],
    #     generator_public_key=genesis_block['generatorPublicKey'],
    #     block_signature=genesis_block['blockSignature'],
    # )

    # for index, transaction in enumerate(genesis_block['transactions']):
    #     TransactionFactory(
    #         id=transaction['id'],
    #         version=transaction['version'],
    #         block_id=genesis_block['id'],
    #         sequence=index,
    #         timestamp=transaction['timestamp'],
    #         sender_public_key=transaction['senderPublicKey'],
    #         recipient_id=transaction['recipientId'],
    #         type=transaction['type'],
    #         amount=transaction['amount'],
    #         fee=transaction['fee'],
    #     )


@pytest.fixture
def redis():
    print('Flush redis')
    redis = Redis(
        host=os.environ.get("REDIS_HOST", "localhost"),
        port=os.environ.get("REDIS_PORT", 6379),
        db=os.environ.get("REDIS_DB", 0),
    )
    redis.flushall()
    return redis


@pytest.fixture(scope="session")
def migrated():
    print('Migrate')
    Database()
    migrate()


@pytest.fixture
def empty_db(migrated):
    print('Clear')
    _clear_db()


@pytest.fixture(scope="session")
def db(migrated):
    print("executed db")
    _clear_db()
    _create_genesis_block()


@pytest.fixture(scope="session")
def app():
    print("executed app")
    return create_app()


@pytest.fixture
def p2p_service(db, app):
    client = app.test_client()
    yield client
