import logging
from binascii import unhexlify

from chain.crypto.utils import verify_hash

from .base import BaseTransaction

logger = logging.getLogger(__name__)


class MultiSignatureTransaction(BaseTransaction):
    def _verify_transaction_signatures(self, public_key):
        for signature in self.signatures:
            transaction_bytes = self.get_bytes(
                skip_signature=True, skip_second_signature=True
            )
            is_verified = verify_hash(
                transaction_bytes,
                unhexlify(signature.encode("utf-8")),
                unhexlify(public_key.encode("utf-8")),
            )
            if is_verified:
                return signature

    def _verify_signatures(self):
        multisignature = self.asset["multisignature"]
        if not self.signatures or len(self.signatures) < multisignature["min"]:
            return False

        keysgroup = []
        for key in multisignature["keysgroup"]:
            if key.startswith("+"):
                keysgroup.append(key[1:])
            else:
                keysgroup.append(key)

        num_valid_signatures = 0
        for key in keysgroup:
            signature = self._verify_transaction_signatures(self, key)
            if signature:
                num_valid_signatures += 1
                if num_valid_signatures == multisignature["min"]:
                    return True
        return False

    def can_be_applied_to_wallet(self, wallet, wallet_manager, block_height):
        if wallet.multisignature:
            logger.error("Multisignature is already registered for this wallet")
            return False

        keysgroup = self.asset["multisignature"]["keysgroup"]
        min_length = self.asset["multisignature"]["min"]
        if len(keysgroup) < min_length:
            logger.error("Specified key count does not meet minimum key count")
            return False

        if len(keysgroup) != len(self.signatures):
            logger.error("Specified key count does not equal signature count")
            return False

        if not self._verify_signatures():
            logger.error("Failed to verify multi-signatures")
            return False

        return super().can_be_applied_to_wallet(wallet, wallet_manager, block_height)

    def apply_to_sender_wallet(self, wallet):
        super().apply_to_sender_wallet(wallet)
        wallet.multisignature = self.asset["multisignature"]

    def revert_for_sender_wallet(self, wallet):
        super().revert_for_sender_wallet(wallet)
        wallet.multisignature = None
