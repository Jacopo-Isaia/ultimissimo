from dataclasses import dataclass


@dataclass
class Product:
    product_id: int
    product_name: str
    brand_id: int
    category_id: int
    model_year: int
    list_price: float

    def __hash__(self):
        return hash(self.product_id)

    def __eq__(self, other):
        return isinstance(other, Product) and self.product_id == other.product_id

    def __str__(self):
        return f"{self.product_name} ({self.product_id})"
