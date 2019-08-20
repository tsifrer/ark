import os

import pytest

from redis import Redis

from chain.common.config import config
from chain.crypto.objects.block import Block as CryptoBlock
from chain.plugins.database.database import Database
from chain.plugins.database.migrate import migrate
from chain.plugins.database.models.block import Block
from chain.plugins.database.models.pool_transaction import PoolTransaction
from chain.plugins.database.models.round import Round
from chain.plugins.database.models.transaction import Transaction

from tests.chain.fixtures import (  # noqa
    crypto_block,
    crypto_transaction,
    crypto_transaction_2,
    dummy_block,
    dummy_block_full_hash,
    dummy_block_hash,
    dummy_transaction,
    dummy_transaction_2,
    dummy_transaction_hash,
)


def _clear_db():
    Round.delete().execute()
    Transaction.delete().execute()
    Block.delete().execute()
    PoolTransaction.delete().execute()


def _create_genesis_block():
    _clear_db()
    block = CryptoBlock.from_dict(config.genesis_block)

    db_block = Block.from_crypto(block)
    db_block.save(force_insert=True)

    for transaction in block.transactions:
        db_trans = Transaction.from_crypto(transaction)
        db_trans.save(force_insert=True)


@pytest.fixture
def redis():
    redis = Redis(
        host=os.environ.get("REDIS_HOST", "localhost"),
        port=os.environ.get("REDIS_PORT", 6379),
        db=os.environ.get("REDIS_DB", 0),
    )
    redis.flushall()
    yield redis
    redis.flushall()


@pytest.fixture(scope="session")
def migrated():
    Database()
    migrate()


@pytest.fixture
def empty_db(migrated):
    _clear_db()
    yield None
    _clear_db()


@pytest.fixture
def db(empty_db):
    _clear_db()
    print("Creating genesis block")
    _create_genesis_block()
