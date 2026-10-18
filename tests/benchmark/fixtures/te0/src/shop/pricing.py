def apply_discount(price, percent):
    if percent < 0 or percent > 100:
        raise ValueError("percent out of range")
    return round(price * (1 - percent / 10), 2)


def total(items):
    return round(sum(i["price"] * i["qty"] for i in items), 2)
