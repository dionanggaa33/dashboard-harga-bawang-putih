"""Antarmuka load ke warehouse."""
from warehouse.loader import load_warehouse

def load(harga, jisdor):
    return load_warehouse(harga, jisdor)
