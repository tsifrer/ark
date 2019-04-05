from binary.unsigned_integer import read_bit32, read_bit64, read_bit8


# TODO: Put this into binary package
class ByteBuffer(bytearray):
    def read_uint8(self):
        return read_bit8(self)

    def read_uint32(self):
        return read_bit32(self)

    def read_uint64(self):
        return read_bit64(self)

    def read_bytes(self, num_bytes, offset=0):
        return bytes(self[offset : offset + num_bytes])

    def pop_uint8(self):
        data = read_bit8(self)
        del self[:1]
        return data

    def pop_uint32(self):
        data = read_bit32(self)
        del self[:4]
        return data

    def pop_uint64(self):
        data = read_bit64(self)
        del self[:8]
        return data

    def pop_bytes(self, num_bytes):
        data = self[:num_bytes]
        del self[:num_bytes]
        return bytes(data)
