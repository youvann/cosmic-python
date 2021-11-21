from typing import Set

import pytest

import model
import services
from repository import AbstractRepository


class FakeRepository(AbstractRepository):
    def __init__(self, batches: Set[model.Batch]):
        self._batches = batches

    def add(self, batch: model.Batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(batch for batch in self._batches if batch.reference == reference)

    def list(self):
        return list(self._batches)


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_returns_allocation():
    line = model.OrderLine("o1", "COMPLICATED-LAMP", 10)
    batch = model.Batch("b1", "COMPLICATED-LAMP", 100, eta=None)
    repo = FakeRepository([batch])

    result = services.allocate(line, repo, FakeSession())
    assert result == "b1"


def test_error_for_invalid_sku():
    line = model.OrderLine("o1", "NONEXISTENTSKU", 10)
    batch = model.Batch("b1", "AREALSKU", 100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate(line, repo, FakeSession())


def test_error_for_out_of_stock():
    line = model.OrderLine("o1", "COMPLICATED-LAMP", 20)
    batch = model.Batch("b1", "COMPLICATED-LAMP", 10, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(
        model.OutOfStock, match="Out of stock for sku COMPLICATED-LAMP"
    ):
        services.allocate(line, repo, FakeSession())


def test_commits():
    line = model.OrderLine("o1", "OMINOUS-MIRROR", 10)
    batch = model.Batch("b1", "OMINOUS-MIRROR", 100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    services.allocate(line, repo, session)
    assert session.committed is True
