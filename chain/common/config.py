import json
import os
from hashlib import sha256
from operator import itemgetter

# TODO: Move this module to common or somewhere else


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(dict, metaclass=SingletonMeta):
    """Object that holds all the configuration for the chain
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        folder = os.environ.get("CHAIN_CONFIG_FOLDER", "config")

        with open(os.path.join(folder, "genesis_block.json")) as f:
            genesis_block = json.loads(f.read())
            for transaction in genesis_block["transactions"]:
                transaction["version"] = 1
            self.genesis_block = genesis_block

        with open(os.path.join(folder, "network.json")) as f:
            self.network = json.loads(f.read())

        with open(os.path.join(folder, "exceptions.json")) as f:
            self.exceptions = json.loads(f.read())

        with open(os.path.join(folder, "peers.json")) as f:
            self.peers = json.loads(f.read())

        # TODO: put this in config file
        self.pool = {
            "max_transaction_characters": 1047876,
            "allowed_senders": [],  # allowed sender public keys
            "max_transactions_per_sender": 300,
            "max_transactions_in_pool": 100000,
            "max_transaction_age": 21600,
            "dynamic_fees": {
                "enabled": True,
                "min_fee_pool": 1000,
                "min_fee_broadcast": 1000,
                # TODO: Put this addon_for_type setting to each transaction so new
                # transactions can be easily added without changing this config
                "addon_bytes_for_type": {
                    "0": 100,  # transfer
                    "1": 250,  # second signature
                    "2": 400000,  # delegate registration
                    "3": 100,  # vote
                    "4": 500,  # multi signature
                    "5": 250,  # ipfs
                    "6": 500,  # timelock transfer
                    "7": 500,  # multi payment
                    "8": 400000,  # delegate resignation
                },
            },
        }

        #     /**
        #  * The list of IPs can access the remote/internal API.
        #  *
        #  * This should usually only include your localhost to grant access to
        #  * the internal API to your forger. If you run a split relay and forger
        #  * you will need to specify the IP of your forger here.
        #  */
        # remoteAccess: ["127.0.0.1", "::ffff:127.0.0.1"],
        self.p2p = {"remote_access": []}

        with open(os.path.join(folder, "milestones.json")) as f:
            milestones = json.loads(f.read())
        milestones.sort(key=itemgetter("height"))
        self.milestones = milestones
        self.milestone_hash = self._calculate_milestone_hash(milestones)

    def _calculate_milestone_hash(self, milestones):
        milestones_json = json.dumps(milestones)
        sha_hash = sha256(milestones_json.encode("utf-8")).hexdigest()
        return sha_hash[:16]

    def get_milestone(self, height):
        for milestone in reversed(self.milestones):
            if height >= milestone["height"]:
                return milestone


config = Config()
