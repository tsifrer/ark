class Field(object):
    accepted_types = None

    def __init__(self, attr, required=True, default=None):
        """
        `attr` is the json field name e.g. previousBlockHex
        """
        super().__init__()
        self.attr = attr
        self.required = required
        self._default = default

    @property
    def default(self):
        return self._default

    @staticmethod
    def to_value(value):
        return value

    @staticmethod
    def to_json_value(value):
        return value


class DictField(Field):
    def __init__(self, attr, required=True):
        super().__init__(attr, required)

    @property
    def default(self):
        return {}


class ListField(Field):
    def __init__(self, attr, required=True):
        super().__init__(attr, required)

    @property
    def default(self):
        return []


class BigIntField(Field):
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


class IntField(Field):
    accepted_types = (str, int)

    @staticmethod
    def to_value(value):
        if value is None:
            return None
        return int(value)


class StrField(Field):
    accepted_types = (str, bytes)

    @staticmethod
    def to_value(value):
        if value is None:
            return None
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return value


class BytesField(Field):
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


class CryptoObjectMeta(type):
    @staticmethod
    def _compile_fields(field_map, serializer_cls):
        fields = []
        for name, field in field_map.items():
            field.name = name
            fields.append(field)
        return fields

    def __call__(cls, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)
        # Set fields on object and set default values
        for field in obj._fields:
            setattr(obj, field.name, field.default)
        return obj

    def __new__(cls, name, bases, attrs):
        fields = {}
        # Take all the Fields from the attributes.
        for attr_name, field in attrs.items():
            if isinstance(field, Field):
                fields[attr_name] = field

        real_cls = super().__new__(cls, name, bases, attrs)
        real_cls._fields = cls._compile_fields(fields, real_cls)
        return real_cls


class CryptoObject(object, metaclass=CryptoObjectMeta):
    pass
