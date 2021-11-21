from datetime import date

import pytest

from domain.model import Batch, OrderLine


def make_batch_and_line(sku, batch_qty, line_qty):
    return (
        Batch("batch-001", sku, batch_qty, eta=date.today()),
        OrderLine("order-123", sku, line_qty),
    )


def test_allocating_to_a_batch_reduces_the_available_quantity():
    # given
    batch = Batch(ref="batch_001", sku="table_A", qty=20, eta=date.today())
    order_line = OrderLine(order_id="order_ref", sku="table_A", qty=2)

    # when
    batch.allocate(order_line)

    # then
    assert batch.available_quantity == 18


def test_can_allocate_if_available_is_greater_than_required():
    large_batch, small_line = make_batch_and_line(
        "ELEGANT_LAMP", batch_qty=20, line_qty=2
    )
    assert large_batch.can_allocate(small_line)


def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_line = make_batch_and_line(
        "ELEGANT_LAMP", batch_qty=2, line_qty=20
    )
    assert small_batch.can_allocate(large_line) is False


def test_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line("ELEGANT_LAMP", batch_qty=2, line_qty=2)
    assert batch.can_allocate(line)


def test_cannot_allocate_if_skus_does_not_match():
    batch = Batch(ref="batch-001", sku="CHAIR", qty=2, eta=None)
    different_sku_line = OrderLine(order_id="order-123", sku="toaster", qty=1)
    assert batch.can_allocate(different_sku_line) is False


def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("DECORATIVE", 20, 2)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 20


def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("AMGULAR-DESK", batch_qty=20, line_qty=2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18


if __name__ == "__main__":
    pytest.main([__file__])
