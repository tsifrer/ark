from binascii import unhexlify

from chain.config import Config
from chain.crypto.address import address_from_public_key
from chain.crypto.constants import (
    TRANSACTION_TYPE_DELEGATE_REGISTRATION,
    TRANSACTION_TYPE_DELEGATE_RESIGNATION,
    TRANSACTION_TYPE_MULTI_PAYMENT,
    TRANSACTION_TYPE_MULTI_SIGNATURE,
    TRANSACTION_TYPE_SECOND_SIGNATURE,
    TRANSACTION_TYPE_VOTE,
)
from chain.crypto.utils import verify_hash


# TODO: there might be a better place for this. Maybe not though. Who knows.
class Wallet(object):
    # TODO: make this mapping better
    # field name, default
    fields = [
        ("address", None),
        ("public_key", None),
        ("second_public_key", None),
        ("multisignature", None),
        ("vote", None),
        ("username", None),
        ("balance", 0),
        ("vote_balance", 0),
        ("produced_blocks", 0),
        ("missed_blocks", 0),
        ("forged_fees", 0),
        ("forged_rewards", 0),
    ]

    def __init__(self, data):
        for field, default in self.fields:
            setattr(self, field, data.get(field, default))

    def _verify_transaction_signatures(self, transaction, public_key):
        for signature in transaction.signatures:
            transaction_bytes = transaction.get_bytes(
                skip_signature=True, skip_second_signature=True
            )
            is_verified = verify_hash(
                transaction_bytes,
                unhexlify(signature.encode("utf-8")),
                unhexlify(public_key.encode("utf-8")),
            )
            if is_verified:
                return signature

    def _verify_signatures(self, transaction):
        multisignature = transaction.asset["multisignature"]
        if (
            not transaction.signatures
            or len(transaction.signatures) < multisignature["min"]
        ):
            return False

        keysgroup = []
        for key in multisignature["keysgroup"]:
            if key.startswith("+"):
                keysgroup.append(key[1:])
            else:
                keysgroup.append(key)

        num_valid_signatures = 0
        for key in keysgroup:
            signature = self._verify_transaction_signatures(transaction, key)
            if signature:
                num_valid_signatures += 1
                if num_valid_signatures == multisignature["min"]:
                    return True
        return False

    def can_apply(self, transaction, block):
        # TODO: transaction schema validation
        # const validationResult = transactionValidator.validate(transaction);
        # if (validationResult.fails) {
        #     errors.push(validationResult.fails.message);
        #     return false;
        # }
        errors = []
        if self.multisignature:
            errors.append("Wallet has multisignature")

        transaction_cost = transaction.amount + transaction.fee
        balance_after = self.balance - transaction_cost
        if balance_after < 0:
            errors.append("Insufficient balance in the wallet")

        if transaction.sender_public_key != self.public_key:
            errors.append(
                "Wallets public_key does not match transactions sender_public_key"
            )

        has_signature = transaction.second_signature or transaction.sign_signature
        if not self.second_public_key and has_signature:
            config = Config()
            milestone = config.get_milestone(block.height)
            # Accept invalid second signature fields prior the applied patch
            if not milestone["ignoreInvalidSecondSignatureField"]:
                errors.append("Invalid second-signature field")

        if self.second_public_key and not transaction.verify_second_signature(
            self.second_public_key
        ):
            errors.append("Failed to verify second-signature")

        # Validation based on transaction types
        if transaction.type == TRANSACTION_TYPE_DELEGATE_REGISTRATION:
            username = transaction.asset["delegate"]["username"]
            # TODO: Checking whether the username is a lowercase version of itself
            # seems silly. Why can't we mutate it to lowercase
            is_valid_username = (
                not self.username and username and username == username.lower()
            )
            if not is_valid_username:
                errors.append("Wallet already has a registered username")

        elif transaction.type == TRANSACTION_TYPE_DELEGATE_RESIGNATION:
            if not self.username:
                errors.append("Wallet hasn't registered a username")

        elif transaction.type == TRANSACTION_TYPE_MULTI_PAYMENT:
            payments_amount = 0
            for payment in transaction.asset["payments"]:
                payments_amount += payment["amount"]

            transaction_cost = payments_amount + transaction.fee
            balance_after = self.balance - transaction_cost
            if balance_after < 0:
                errors.append(
                    "Insufficient balance in the wallet to transfer all payments"
                )

        elif transaction.type == TRANSACTION_TYPE_MULTI_SIGNATURE:
            keysgroup = transaction.asset["multisignature"]["keysgroup"]
            min_length = transaction.asset["multisignature"]["min"]
            if len(keysgroup) < min_length:
                errors.append("Specified key count does not meet minimum key count")

            if len(keysgroup) != len(transaction.signatures):
                errors.append("Specified key cound toes not equal signature count")

            if not self._verify_signatures(transaction):
                errors.append("Failed to verify multi-signatures")

        elif transaction.type == TRANSACTION_TYPE_SECOND_SIGNATURE:
            if self.second_public_key:
                errors.append("Wallet already has a second signature")

        elif transaction.type == TRANSACTION_TYPE_VOTE:
            vote = transaction.asset["votes"][0]

            if vote.startswith("-"):
                if not self.vote:
                    errors.append("Wallet has not voted yet")
                elif self.vote != vote[1:]:
                    errors.append(
                        "The unvote public key does not match the currently voted one"
                    )
            if vote.startswith("+") and self.vote:
                errors.append("Wallet has already voted")

        can_apply = True if len(errors) == 0 else False
        return can_apply, errors

    def apply_transaction_to_sender(self, transaction):
        address = address_from_public_key(transaction.sender_public_key)
        is_correct_wallet = (
            transaction.sender_public_key == self.public_key or address == self.address
        )
        if is_correct_wallet:
            self.balance -= transaction.amount
            self.balance -= transaction.fee

        # apply specific stuff based on transaction type
        if transaction.type == TRANSACTION_TYPE_DELEGATE_REGISTRATION:
            self.username = transaction.asset["delegate"]["username"]

        elif transaction.type == TRANSACTION_TYPE_MULTI_SIGNATURE:
            self.multisignature = transaction.asset["multisignature"]

        elif transaction.type == TRANSACTION_TYPE_SECOND_SIGNATURE:
            self.second_public_key = transaction.asset["signature"]["publicKey"]

        elif transaction.type == TRANSACTION_TYPE_VOTE:
            vote = transaction.asset["votes"][0]
            if vote.startswith("+"):
                self.vote = vote[1:]
            elif vote.startswith("-"):
                self.vote = None

    def apply_transaction_to_recipient(self, transaction):
        if transaction.recipient_id == self.address:
            self.balance += transaction.amount

    def apply_block(self, block):
        address = address_from_public_key(block.generator_public_key)
        is_correct_wallet = (
            block.generator_public_key == self.public_key or address == self.address
        )
        if is_correct_wallet:
            self.balance += block.reward
            self.balance += block.total_fee

            self.produced_blocks += 1
            self.forged_fees += block.total_fee
            self.forged_rewards += block.reward
        else:
            raise Exception(
                "Couldn't apply block {} to wallet {}".format(block.id, self.public_key)
            )

    def revert_transaction_for_sender(self, transaction):
        address = address_from_public_key(transaction.sender_public_key)
        is_correct_wallet = (
            transaction.sender_public_key == self.public_key or address == self.address
        )
        if is_correct_wallet:
            self.balance -= transaction.amount
            self.balance -= transaction.fee

        # revert specific stuff based on transaction type
        if transaction.type == TRANSACTION_TYPE_DELEGATE_RESIGNATION:
            self.username = None

        elif transaction.type == TRANSACTION_TYPE_MULTI_SIGNATURE:
            self.multisignature = None

        elif transaction.type == TRANSACTION_TYPE_SECOND_SIGNATURE:
            self.second_public_key = None

        elif transaction.type == TRANSACTION_TYPE_VOTE:
            vote = transaction.asset["votes"][0]
            if vote.startswith("+"):
                self.vote = None
            elif vote.startswith("-"):
                self.vote = vote[1:]

    def revert_transaction_for_recipient(self, transaction):
        if transaction.recipient_id == self.address:
            self.balance -= transaction.amount

    def revert_block(self, block):
        address = address_from_public_key(block.generator_public_key)
        if block.generator_public_key == self.public_key and address == self.address:
            self.balance -= block.reward + block.total_fee

            self.forged_fees -= block.total_fee
            self.forged_rewards -= block.reward
        else:
            raise Exception(
                "Couldn't revert block {} for wallet {}".format(
                    block.id, self.public_key
                )
            )
