class CryptoField(object):

    def __init__(self, attr, required=True, default=None, field_type=None):
        """
        `attr` is the json field name e.g. previousBlockHex
        """
        super().__init__()
        self.attr = attr
        self.required = required
        self.default = default
        self.type = field_type


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
            if isinstance(field, CryptoField):
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
