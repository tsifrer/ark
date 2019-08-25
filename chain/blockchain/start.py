import logging

from chain.blockchain.blockchain import Blockchain
from chain.common.log import DEFAULT_LOGGING

if __name__ == "__main__":
    # Setup logging
    logging.config.dictConfig(DEFAULT_LOGGING)

    bc = Blockchain()
    bc.start()
