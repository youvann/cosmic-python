import abc
from typing import Set

import model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    def get(self, reference) -> model.Batch:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch):
        self.session.add(batch)

    def get(self, reference):
        return self.session.query(model.Batch).filter_by(reference=reference).one()

    def list(self):
        return self.session.query(model.Batch).all()


class FakeRepository(AbstractRepository):
    def __init__(self, batches: Set[model.Batch]):
        self._batches = batches

    def add(self, batch: model.Batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(batch for batch in self._batches if batch.reference == reference)

    def list(self):
        return list(self._batches)
