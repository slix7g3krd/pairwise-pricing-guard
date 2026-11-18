"""Server-side pricing guard.

Core rules:
- Prices always come from the server-side price table, never the client.
- Quantity must be a positive integer; gifts are not orderable line items.
- Stacked discounts are capped.
- Totals are recomputed server-side with a single rounding pass.
- Refunds are based on the amount actually paid.
"""

from decimal import Decimal, ROUND_HALF_UP

BASE_CURRENCY = 'CNY'


def server_price(sku, price_table):
    """Look up the authoritative price for a sku. Unknown skus -> None."""
    return price_table.get(sku)


def validate_quantity(qty, gift=False):
    """Quantity must be a positive integer. Gift items are not valid purchases."""
    if gift:
        return False
    return isinstance(qty, int) and not isinstance(qty, bool) and qty >= 1


def max_discount(discounts, cap):
    """Sum stacked discounts, capped at `cap`."""
    total = sum(discounts)
    return min(total, cap)


def round_money(amount):
    """Round to 2 decimal places, half-up, in exactly one place."""
    cents = Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return float(cents)


def recompute_total(items, price_table, tax=0, shipping=0, currency=BASE_CURRENCY):
    """Recompute the order total server-side.

    Prices come from `price_table`; client-supplied prices are ignored.
    Shipping and tax are applied server-side. Rounding happens once, at
    the order level. Returns None for unsupported currencies.
    """
    if currency != BASE_CURRENCY:
        return None

    subtotal = 0.0
    for item in items:
        price = server_price(item.get('sku'), price_table)
        qty = item.get('qty')
        if price is None or not validate_quantity(qty):
            continue
        subtotal += price * qty

    total = subtotal * (1 + tax) + shipping
    return round_money(total)


def refund_amount(paid, already_refunded=0):
    """Refundable balance based on the amount actually paid, never negative."""
    return max(round_money(paid - already_refunded), 0)
