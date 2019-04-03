from chain.crypto.objects.base import CryptoObject, DictField, ListField


def test_list_field_has_immutable_default_value():
    class TestList(CryptoObject):
        foo = ListField("foo")

    obj = TestList()
    obj.foo.append("bar")
    assert obj.foo == ["bar"]

    obj1 = TestList()
    obj1.foo.append("bar1")
    assert obj1.foo == ["bar1"]

    obj.foo.append("baz")
    assert obj.foo == ["bar", "baz"]


def test_dict_field_has_immutable_default_value():
    class TestList(CryptoObject):
        foo = DictField("foo")

    obj = TestList()
    obj.foo["bar"] = "baz"
    assert list(obj.foo.keys()) == ["bar"]
    assert list(obj.foo.values()) == ["baz"]

    obj1 = TestList()
    obj1.foo["bar1"] = "baz1"
    assert list(obj1.foo.keys()) == ["bar1"]
    assert list(obj1.foo.values()) == ["baz1"]

    obj.foo["baz"] = "omg"
    assert list(obj.foo.keys()) == ["bar", "baz"]
    assert list(obj.foo.values()) == ["baz", "omg"]
