import copy


class FilterRegistry(type):
    REGISTRY = {}

    def __new__(mcs, name, bases, attrs):
        new_cls = type.__new__(mcs, name, bases, attrs)
        mcs.REGISTRY[new_cls.TYPE] = new_cls()
        return new_cls

    @classmethod
    def get_registry(mcs):
        return copy.copy(mcs.REGISTRY)

    @classmethod
    def get_instances(mcs):
        return list(mcs.REGISTRY.values())
