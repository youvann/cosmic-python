from typing import Set

import pytest

from domain import model
from service_layer import services
from adapters.repository import AbstractRepository


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


def test_allocate_returns_allocation():
    repo, session = FakeRepository(set()), FakeSession()
    services.add_batch("b1", "COMPLICATED-LAMP", 100, None, repo, session)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, repo, session)
    assert result == "b1"


def test_error_for_invalid_sku():
    repo, session = FakeRepository(set()), FakeSession()
    services.add_batch("b1", "AREALSKU", 100, None, repo, session)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, repo, session)


def test_error_for_out_of_stock():
    repo, session = FakeRepository(set()), FakeSession()
    services.add_batch("b1", "COMPLICATED-LAMP", 10, None, repo, session)

    with pytest.raises(
        model.OutOfStock, match="Out of stock for sku COMPLICATED-LAMP"
    ):
        services.allocate("o1", "COMPLICATED-LAMP", 20, repo, FakeSession())


def test_commits():
    repo, session = FakeRepository(set()), FakeSession()
    services.add_batch("b1", "OMINOUS-MIRROR", 100, None, repo, session)
    assert session.committed is True


def test_add_batch():
    repo, session = FakeRepository(set()), FakeSession()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, repo, session)
    assert repo.get("b1") is not None
    assert session.committed
