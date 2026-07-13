import networkx as nx

from database.DAO import DAO


class Model:
    def __init__(self):
        self._graph = nx.DiGraph()
        self._idMap = {}
        self._bestPath = []
        self._bestPeso = -1

    def getDateRange(self):
        return DAO.getDateRange()

    def getCategories(self):
        return DAO.getCategories()

    def buildGraph(self, category_id, start, end):
        self._graph.clear()
        self._idMap = {}
        products = DAO.getProductsByCategory(category_id)
        sales = DAO.getSales(category_id, start, end)
        if products is None or sales is None:
            return False
        for p in products:
            self._idMap[p.product_id] = p
        self._graph.add_nodes_from(products)
        venduti = [self._idMap[pid] for pid in sales if pid in self._idMap]
        for i in range(len(venduti)):
            for j in range(i + 1, len(venduti)):
                p1 = venduti[i]
                p2 = venduti[j]
                n1 = sales[p1.product_id]
                n2 = sales[p2.product_id]
                peso = n1 + n2
                if n1 > n2:
                    self._graph.add_edge(p1, p2, weight=peso)
                elif n2 > n1:
                    self._graph.add_edge(p2, p1, weight=peso)
                else:
                    self._graph.add_edge(p1, p2, weight=peso)
                    self._graph.add_edge(p2, p1, weight=peso)
        return True

    def getNumNodes(self):
        return self._graph.number_of_nodes()

    def getNumEdges(self):
        return self._graph.number_of_edges()

    def getNodes(self):
        return sorted(self._graph.nodes, key=lambda p: p.product_name)

    def getProduct(self, product_id):
        return self._idMap.get(product_id)

    def getBestProducts(self):
        result = []
        for node in self._graph.nodes:
            out_w = sum(data["weight"] for _, _, data in self._graph.out_edges(node, data=True))
            in_w = sum(data["weight"] for _, _, data in self._graph.in_edges(node, data=True))
            result.append((node, out_w - in_w))
        result.sort(key=lambda x: x[1], reverse=True)
        return result[:5]

    def getCammino(self, start, end, lun):
        self._bestPath = []
        self._bestPeso = -1
        self._ricorsione([start], end, lun)
        if len(self._bestPath) == 0:
            return None, 0
        return self._bestPath, self._bestPeso

    def _ricorsione(self, parziale, end, lun):
        ultimo = parziale[-1]
        if len(parziale) - 1 == lun:
            if ultimo == end:
                peso = self._pesoCammino(parziale)
                if peso > self._bestPeso:
                    self._bestPeso = peso
                    self._bestPath = list(parziale)
            return
        for succ in self._graph.successors(ultimo):
            if succ not in parziale:
                parziale.append(succ)
                self._ricorsione(parziale, end, lun)
                parziale.pop()

    def _pesoCammino(self, path):
        peso = 0
        for i in range(len(path) - 1):
            peso += self._graph[path[i]][path[i + 1]]["weight"]
        return peso
