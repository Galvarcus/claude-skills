def in_stock(stock, sku):
    return stock.get(sku, 0) > 0
