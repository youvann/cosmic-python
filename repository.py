import abc

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


class SqlRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch: model.Batch):
        self.session.execute(
            "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
            " VALUES (:reference, :sku, :purchased_quantity, :eta)",
            dict(
                reference=batch.reference,
                sku=batch.sku,
                purchased_quantity=batch._purchased_quantity,
                eta=batch.eta,
            ),
        )

    def get(self, reference) -> model.Batch:
        result = self.session.execute(
            "SELECT reference, sku, _purchased_quantity, eta FROM batches where reference=:reference",
            dict(reference=reference),
        )

        return model.Batch(
            ref=result[0]["reference"],
            sku=result[0]["sku"],
            qty=result[0]["_purchased_quantity"],
            eta=result[0]["eta"],
        )
