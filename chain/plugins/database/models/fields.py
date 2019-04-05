from peewee import BlobField


class BytesField(BlobField):
    """This is a BlobField adapted to our needs
    Default BlobField returns memoryview when getting data from the db. We want bytes.
    """

    def adapt(self, value):
        if value and isinstance(value, memoryview):
            return value.tobytes()
        return value
