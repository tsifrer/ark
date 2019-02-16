from binascii import unhexlify

from coincurve import PublicKey


def verify_hash(message, signature, public_key):
    if not isinstance(signature, bytes):
        signature = unhexlify(signature)
    if not isinstance(public_key, bytes):
        public_key = unhexlify(public_key)

    pub_key = PublicKey(public_key)
    is_verified = pub_key.verify(signature, message)
    return is_verified
