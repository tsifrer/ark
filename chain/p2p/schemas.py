import avocato


class GetBlocksSchema(avocato.AvocatoObject):
    """Schema for p2p.peer.getBlocks
    """

    last_block_height = avocato.IntField(attr="lastBlockHeight", required=True)
    block_limit = avocato.IntField(attr="blockLimit", required=False, default=400)
    headers_only = avocato.BoolField(attr="headersOnly", required=False, default=False)
    serialized = avocato.BoolField(required=False, default=False)
