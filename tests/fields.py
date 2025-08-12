import factory
from factory import Factory


class ListSubFactory(factory.declarations.LazyAttribute):
    def __init__(self, factory_class: type[Factory], size: int = 1, **kwargs: dict) -> None:
        self.factory_class = factory_class
        self.size = size
        self.kwargs = kwargs
        super().__init__(self._make_list)

    def _make_list(self, _: Factory) -> list[Factory]:
        return self.factory_class.create_batch(self.size, **self.kwargs)
