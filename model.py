from dataclasses import dataclass
from datetime import date
from typing import Optional, Set, List


@dataclass(unsafe_hash=True)
class OrderLine:
    """
    OrderLine is a value object
    """

    order_id: str
    sku: str
    qty: int


class Batch:
    """
    Batch is an entity
    We can allocate lines to a batch, or change the date that we expect it to arrive,
    and it will still be the same entity.
    """

    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date]):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations: Set[OrderLine] = set()

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return self.reference == other.reference

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other: "Batch"):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta


class OutOfStock(Exception):
    pass


def allocate(line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = next(batch for batch in sorted(batches) if batch.can_allocate(line))
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")
    batch.allocate(line)
    return batch.reference
