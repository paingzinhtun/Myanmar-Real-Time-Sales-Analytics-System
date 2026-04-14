from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Store:
    store_id: str
    store_name: str
    city: str
    region: str


@dataclass(frozen=True)
class Product:
    product_id: str
    product_name: str
    category: str
    unit_price_mmk: int


STORES = [
    Store("STR-001", "Yangon Downtown Mart", "Yangon", "Yangon Region"),
    Store("STR-002", "Mandalay Smart Shop", "Mandalay", "Mandalay Region"),
    Store("STR-003", "Naypyidaw Capital Store", "Naypyidaw", "Naypyidaw Union Territory"),
    Store("STR-004", "Taunggyi Family Choice", "Taunggyi", "Shan State"),
    Store("STR-005", "Mawlamyine City Market", "Mawlamyine", "Mon State"),
    Store("STR-006", "Bago Daily Needs", "Bago", "Bago Region"),
    Store("STR-007", "Pathein Riverside Retail", "Pathein", "Ayeyarwady Region"),
]

PRODUCTS = [
    Product("PRD-001", "Shan Tea Mix", "Groceries", 2800),
    Product("PRD-002", "Thanaka Skincare Set", "Beauty", 12500),
    Product("PRD-003", "Phone Power Bank", "Electronics", 38500),
    Product("PRD-004", "Rice Cooker 1.8L", "Home Appliances", 89500),
    Product("PRD-005", "School Backpack", "Lifestyle", 22000),
    Product("PRD-006", "Instant Mohinga Pack", "Groceries", 4500),
    Product("PRD-007", "LED Study Lamp", "Home Appliances", 17500),
    Product("PRD-008", "Bluetooth Earbuds", "Electronics", 42000),
    Product("PRD-009", "Cotton Longyi", "Fashion", 16000),
    Product("PRD-010", "Water Purifier Jug", "Household", 31000),
]

PAYMENT_METHODS = [
    "Cash on Delivery",
    "KBZPay",
    "Wave Pay",
    "AYA Pay",
    "CB Pay",
    "Bank Transfer",
]

DEVICE_TYPES = ["Android", "iPhone", "Web", "Tablet"]
ORDER_STATUSES = ["confirmed", "packed", "shipped", "delivered"]
