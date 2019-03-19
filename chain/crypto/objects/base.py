class Field(object):
    accepted_types = None

    def __init__(self, attr, required=True, default=None):
        """
        `attr` is the json field name e.g. previousBlockHex
        """
        super().__init__()
        self.attr = attr
        self.required = required
        self.default = default

    @staticmethod
    def to_value(value):
        return value

    @staticmethod
    def to_json_value(value):
        return value


class BigIntField(Field):
    """
    Python doesn't need this field. It's here because we need to convert int to str
    when responding as json, so other nodes know what we're doing.
    """
    accepted_types = (str, int)

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
            return value.decode('utf-8')
        return value


class BytesField(Field):
    accepted_types = (str, bytes)

    @staticmethod
    def to_value(value):
        if value is None:
            return None
        if isinstance(value, str):
            return value.encode('utf-8')
        return value

    @staticmethod
    def to_json_value(value):
        if value is None:
            return value
        return value.decode('utf-8')


class CryptoObjectMeta(type):
    @staticmethod
    def _compile_fields(field_map, serializer_cls):
        fields = []

        for name, field in field_map.items():
            field.name = name
            fields.append(field)
        return fields

    def __new__(cls, name, bases, attrs):
        fields = {}
        # Take all the Fields from the attributes.
        for attr_name, field in attrs.items():
            if isinstance(field, Field):
                fields[attr_name] = field

        real_cls = super().__new__(cls, name, bases, attrs)
        compiled_fields = cls._compile_fields(fields, real_cls)
        real_cls._fields = compiled_fields

        # Set fields on object and set default values
        for field in compiled_fields:
            setattr(real_cls, field.name, field.default)

        return real_cls


class CryptoObject(object, metaclass=CryptoObjectMeta):
    pass
