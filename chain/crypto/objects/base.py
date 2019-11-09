import operator


class Field(object):
    """:class:`Field` handles converting between primitive values and internal datatypes. It also
    deals with validating input values.

    :param str attr: The attribute to get on the object. If this is not supplied, the name this
        field was assigned to on the serializer will be used.
    :param str label: A label to use as the name of the serialized field instead of using the
        attribute name of the field.
    :param bool required: Whether the field is required.
    """

    getter_takes_serializer = False
    accepted_types = None

    def __init__(self, attr=None, required=True, default=None):
        self.attr = attr
        self.required = required
        self._default = default

    @property
    def default(self):
        """Function that retuns default value. If the default is mutable object, override
        this function and return default mutable object
        """
        return self._default

    @staticmethod
    def to_value(value):
        return value

    @staticmethod
    def serialize(value):
        """Transform to serialized value.
        """
        return value


class StrField(Field):
    """Converts input value to string.

    :param int max_length: Maximum lenght of the string. If present, adds a validator for max lenght
        which will be run when ``is_valid`` method on the serializer is called.
    :param int min_length: Minimum lenght of the string. If present, adds a validator for min lenght
        which will be run when ``is_valid`` method on the serializer is called.
    :param list choices: Available choices. If present, adds a validator that checks if value is
        present in choices and will be run when ``is_valid`` method on the serializer is called.
    """

    accepted_types = (str, bytes)

    @staticmethod
    def to_value(value):
        if value is None:
            return None
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return value

    @staticmethod
    def serialize(value):
        """Transform to serialized value.
        """
        if value is None:
            return value
        return str(value)


class IntField(Field):
    """Converts input value to integer.
    """

    accepted_types = (str, int)

    @staticmethod
    def to_value(value):
        if value is None:
            return None
        return int(value)

    @staticmethod
    def serialize(value):
        """Transform to serialized value.
        """
        if value is None:
            return value
        return int(value)


class DictField(Field):
    """Converts input value to dict.
    """

    accepted_types = (dict,)

    @property
    def default(self):
        return {}

    @staticmethod
    def serialize(value):
        """Transform to serialized value.
        """
        if value is None:
            return value
        return dict(value)


class ListField(Field):
    @property
    def default(self):
        return []

    @staticmethod
    def serialize(value):
        """Transform to serialized value.
        """
        if value is None:
            return value
        return list(value)


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
    def serialize(value):
        """Transform to serialized value.
        """
        if value is None:
            return value
        return str(value)


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
    def serialize(value):
        """Transform to serialized value.
        """
        if value is None:
            return value
        return value.decode("utf-8")


# TODO: try and refactor this
def _compile_fields(field, name, object_cls):
    getter = operator.itemgetter(field.attr or name)

    # Set the field name to a supplied label; defaults to the attribute name.
    field.name = name
    field._getter = getter
    return field


class BaseObjectMeta(type):
    @staticmethod
    def _get_fields_from_base_classes(object_cls):
        fields = []
        # Get all the fields from base classes.
        for cls in object_cls.__mro__[::-1]:
            if isinstance(cls, BaseObjectMeta):
                fields += cls._fields
        return fields

    @staticmethod
    def _compile_fields(field_map, object_cls):
        return [
            _compile_fields(field, name, object_cls)
            for name, field in field_map.items()
        ]

    def __new__(cls, name, bases, attrs):
        # Fields declared directly on the class.
        direct_fields = {}

        # Take all the Fields from the attributes.
        for attr_name, field in attrs.items():
            if isinstance(field, Field):
                direct_fields[attr_name] = field
        for k in direct_fields.keys():
            del attrs[k]

        real_cls = super().__new__(cls, name, bases, attrs)
        compiled_fields = cls._compile_fields(direct_fields, real_cls)

        base_classes_fields = cls._get_fields_from_base_classes(real_cls)

        all_fields = compiled_fields + base_classes_fields
        real_cls._fields = all_fields
        real_cls._field_map = {x.name: x for x in all_fields}
        return real_cls


class BaseObject(Field, metaclass=BaseObjectMeta):
    _fields = []

    def __init__(self, data=None, instance=None, **kwargs):
        super().__init__()
        if data:
            if not isinstance(data, dict):
                raise TypeError("data must be dict")
            self._populate_from_dict(data)
        elif instance:
            self._populate_from_instance(instance)
        else:
            self._populate_with_default_values(kwargs)

    def __setattr__(self, name, value, validate_required=True):
        if name in self._field_map:
            field = self._field_map[name]
            if validate_required and field.required and value is None:
                raise ValueError('Attribute "{}" is required'.format(field.name))
            if (
                value is not None
                and field.accepted_types
                and not isinstance(value, field.accepted_types)
            ):
                raise TypeError(
                    "Attribute {} ({}) must be of type {}".format(
                        field.name, type(value), field.accepted_types
                    )
                )
            value = field.to_value(value)

        super().__setattr__(name, value)

    def _populate_from_instance(self, instance):
        for field in self._fields:
            self.__setattr__(field.name, getattr(instance, field.name, field.default))

    def _populate_from_dict(self, data):
        for field in self._fields:
            self.__setattr__(field.name, data.get(field.attr, field.default))

    def _populate_with_default_values(self, data):
        # Don't validate required to allow creation of empty objects
        for field in self._fields:
            self.__setattr__(
                field.name, data.get(field.name, field.default), validate_required=False
            )
