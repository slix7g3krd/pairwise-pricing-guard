from security.pricing_guard import (
    server_price,
    validate_quantity,
    max_discount,
    recompute_total,
    round_money,
    refund_amount
)


def test_price():
    assert server_price('A', {'A': 100}) == 100

def test_unknown():
    assert server_price('Z', {'A': 100}) is None

def test_qty_ok():
    assert validate_quantity(1) is True

def test_qty_zero():
    assert validate_quantity(0) is False

def test_qty_neg():
    assert validate_quantity(-1) is False

def test_discount():
    assert max_discount([0.2, 0.3], 0.5) == 0.5

def test_discount_over():
    assert max_discount([0.2, 0.4], 0.5) == 0.5

def test_round():
    assert round_money(10.005) == 10.01

def test_total():
    assert recompute_total([{'sku': 'A', 'qty': 2}], {'A': 100}) == 200

def test_tax():
    assert recompute_total([{'sku': 'A', 'qty': 1}], {'A': 100}, tax=0.1) == 110

def test_shipping():
    assert recompute_total([{'sku': 'A', 'qty': 1}], {'A': 100}, shipping=10) == 110

def test_refund():
    assert refund_amount(100, 20) == 80

def test_currency():
    assert recompute_total([{'sku': 'A', 'qty': 1}], {'A': 100}, currency='USD') is None

def test_gift():
    assert validate_quantity(1, gift=True) is False

def test_empty():
    assert recompute_total([], {'A': 100}) == 0
