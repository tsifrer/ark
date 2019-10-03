import avocato


class Field(avocato.Field):
    pass


class DictField(avocato.DictField):
    pass


class ListField(avocato.ListField):
    pass


class BigIntField(avocato.Field):
    """
    Python doesn't need this field. It's here because we need to convert int to str
    when responding as json, so other nodes know what we're doing.
    """

    accepted_types = (str, int)

    @property
    def default(self):
        return 0

    @staticmethod
    def to_value(value):
        if value is None:
            return None
        return int(value)

    @staticmethod
    def to_json_value(value):
        if value is None:
            return value
        return str(value)


class IntField(avocato.Field):
    accepted_types = (str, int)

    @staticmethod
    def to_value(value):
        if value is None:
            return None
        return int(value)


class StrField(avocato.Field):
    accepted_types = (str, bytes)

    @staticmethod
    def to_value(value):
        if value is None:
            return None
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return value


class BytesField(avocato.Field):
    accepted_types = (str, bytes)

    @staticmethod
    def to_value(value):
        if value is None:
            return None
        if isinstance(value, str):
            return value.encode("utf-8")
        return value

    @staticmethod
    def to_json_value(value):
        if value is None:
            return value
        return value.decode("utf-8")
