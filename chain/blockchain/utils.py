from chain.crypto import slots


def is_block_chained(previous_block, next_block):
    print('{} == {}'.format(next_block.previous_block, previous_block.id))
    follows_previous = next_block.previous_block == previous_block.id
    is_plus_one = next_block.height == previous_block.height + 1

    previous_slot = slots.get_slot_number(
        previous_block.height, previous_block.timestamp
    )
    next_slot = slots.get_slot_number(next_block.height, next_block.timestamp)
    is_after_previous_slot = previous_slot < next_slot

    print('follows_previous', follows_previous)
    print('is_plus_one', is_plus_one)
    print('is_after_previous_slot', is_after_previous_slot)
    return follows_previous and is_plus_one and is_after_previous_slot
