import abc
from typing import List

import model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    def get(self, reference) -> model.Batch:
        raise NotImplementedError


class SqlRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch: model.Batch):
        batch_result = self.session.execute(
            "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
            " VALUES (:reference, :sku, :purchased_quantity, :eta)",
            dict(
                reference=batch.reference,
                sku=batch.sku,
                purchased_quantity=batch._purchased_quantity,
                eta=batch.eta,
            ),
        )

        for order_line in batch._allocations:
            order_line_result = self.session.execute(
                "INSERT INTO order_lines (sku, qty, order_id)"
                " VALUES (:sku, :qty, :order_id)",
                dict(
                    sku=order_line.sku,
                    qty=order_line.qty,
                    order_id=order_line.order_id,
                ),
            )

            self.session.execute(
                "INSERT INTO allocations (order_line_id, batch_id)"
                " VALUES (:order_line_id, :batch_id)",
                dict(
                    order_line_id=order_line_result.lastrowid,
                    batch_id=batch_result.lastrowid,
                ),
            )

    def get(self, reference) -> model.Batch:
        batches = self.session.execute(
            'SELECT id, reference, sku, _purchased_quantity, eta FROM "batches" WHERE reference=:reference',
            dict(reference=reference),
        )
        batch = next((dict(b) for b in batches))

        order_lines_raw = self.session.execute(
            "SELECT order_lines.order_id, order_lines.sku, order_lines.qty FROM allocations"
            " JOIN order_lines ON allocations.order_line_id = order_lines.id "
            " WHERE allocations.batch_id=:batch_id",
            dict(batch_id=batch["id"]),
        )
        order_lines: List[model.OrderLine] = [
            model.OrderLine(**dict(o)) for o in order_lines_raw
        ]

        batch = model.Batch(
            ref=batch["reference"],
            sku=batch["sku"],
            qty=batch["_purchased_quantity"],
            eta=batch["eta"],
        )
        for order_line in order_lines:
            batch.allocate(order_line)
        return batch
