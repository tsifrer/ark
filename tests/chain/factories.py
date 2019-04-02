from factory import Factory

from chain.plugins.database.models.block import Block
from chain.plugins.database.models.round import Round
from chain.plugins.database.models.transaction import Transaction


class PeeWeeModelFactory(Factory):
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return model_class.create(*args, **kwargs)


class BlockFactory(PeeWeeModelFactory):
    class Meta:
        model = Block


class TransactionFactory(PeeWeeModelFactory):
    class Meta:
        model = Transaction


class RoundFactory(PeeWeeModelFactory):
    class Meta:
        model = Round
