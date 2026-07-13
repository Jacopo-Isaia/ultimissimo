import mysql.connector

from database.DB_connect import DBConnect
from model.product import Product


class DAO():
    def __init__(self):
        pass

    @staticmethod
    def getDateRange():
        conn = DBConnect.get_connection()
        if conn is None:
            return None, None
        try:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT MIN(order_date) AS first, MAX(order_date) AS last FROM orders"
            cursor.execute(query)
            row = cursor.fetchone()
            cursor.close()
            if row is None:
                return None, None
            return row["first"], row["last"]
        except mysql.connector.Error:
            return None, None
        finally:
            conn.close()

    @staticmethod
    def getCategories():
        conn = DBConnect.get_connection()
        if conn is None:
            return None
        try:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT category_id, category_name FROM categories ORDER BY category_name"
            cursor.execute(query)
            result = [row for row in cursor]
            cursor.close()
            return result
        except mysql.connector.Error:
            return None
        finally:
            conn.close()

    @staticmethod
    def getProductsByCategory(category_id):
        conn = DBConnect.get_connection()
        if conn is None:
            return None
        try:
            cursor = conn.cursor(dictionary=True)
            query = """SELECT product_id, product_name, brand_id, category_id, model_year, list_price
                       FROM products
                       WHERE category_id = %s"""
            cursor.execute(query, (category_id,))
            result = []
            for row in cursor:
                result.append(Product(row["product_id"], row["product_name"], row["brand_id"],
                                      row["category_id"], row["model_year"], row["list_price"]))
            cursor.close()
            return result
        except mysql.connector.Error:
            return None
        finally:
            conn.close()

    @staticmethod
    def getSales(category_id, start, end):
        conn = DBConnect.get_connection()
        if conn is None:
            return None
        try:
            cursor = conn.cursor(dictionary=True)
            query = """SELECT oi.product_id AS pid, COUNT(DISTINCT oi.order_id) AS n
                       FROM order_items oi, orders o, products p
                       WHERE oi.order_id = o.order_id
                         AND oi.product_id = p.product_id
                         AND p.category_id = %s
                         AND DATE(o.order_date) BETWEEN %s AND %s
                       GROUP BY oi.product_id"""
            cursor.execute(query, (category_id, start, end))
            result = {}
            for row in cursor:
                result[row["pid"]] = row["n"]
            cursor.close()
            return result
        except mysql.connector.Error:
            return None
        finally:
            conn.close()
