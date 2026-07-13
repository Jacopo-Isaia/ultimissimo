import datetime

import flet as ft


class Controller:
    def __init__(self, view, model):
        self._view = view
        self._model = model

    def fillDdCategory(self):
        categories = self._model.getCategories()
        if categories is None:
            self._view.create_alert("Errore di connessione al database")
            return
        self._view._ddcategory.options.clear()
        for c in categories:
            self._view._ddcategory.options.append(
                ft.dropdown.Option(key=str(c["category_id"]), text=c["category_name"]))
        self._view.update_page()

    def handleCreaGrafo(self, e):
        category = self._view._ddcategory.value
        if category is None:
            self._view.create_alert("Selezionare una categoria")
            return
        start = self._view._dp1.value
        end = self._view._dp2.value
        if start is None or end is None:
            self._view.create_alert("Selezionare entrambe le date")
            return
        if isinstance(start, datetime.datetime):
            start = start.date()
        if isinstance(end, datetime.datetime):
            end = end.date()
        if start > end:
            self._view.create_alert("La data di inizio deve precedere la data di fine")
            return
        success = self._model.buildGraph(int(category), start, end)
        if not success:
            self._view.create_alert("Errore nell'accesso al database")
            return
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text("Grafo creato correttamente"))
        self._view.txt_result.controls.append(ft.Text(f"Numero di nodi: {self._model.getNumNodes()}"))
        self._view.txt_result.controls.append(ft.Text(f"Numero di archi: {self._model.getNumEdges()}"))
        self._view._ddProdStart.options.clear()
        self._view._ddProdEnd.options.clear()
        self._view._ddProdStart.value = None
        self._view._ddProdEnd.value = None
        for node in self._model.getNodes():
            self._view._ddProdStart.options.append(
                ft.dropdown.Option(key=str(node.product_id), text=node.product_name))
            self._view._ddProdEnd.options.append(
                ft.dropdown.Option(key=str(node.product_id), text=node.product_name))
        self._view.update_page()

    def handleBestProdotti(self, e):
        if self._model.getNumNodes() == 0:
            self._view.create_alert("Creare prima il grafo")
            return
        best = self._model.getBestProducts()
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text("I 5 prodotti più venduti:"))
        for node, delta in best:
            self._view.txt_result.controls.append(ft.Text(f"{node} --> {delta}"))
        self._view.update_page()

    def handleCercaCammino(self, e):
        if self._model.getNumNodes() == 0:
            self._view.create_alert("Creare prima il grafo")
            return
        try:
            lun = int(self._view._txtInLun.value)
        except (ValueError, TypeError):
            self._view.create_alert("Inserire una lunghezza intera valida")
            return
        if lun < 1:
            self._view.create_alert("La lunghezza deve essere maggiore di zero")
            return
        start_id = self._view._ddProdStart.value
        end_id = self._view._ddProdEnd.value
        if start_id is None or end_id is None:
            self._view.create_alert("Selezionare prodotto di partenza e di arrivo")
            return
        start = self._model.getProduct(int(start_id))
        end = self._model.getProduct(int(end_id))
        if start is None or end is None:
            self._view.create_alert("Prodotti selezionati non validi")
            return
        if start == end:
            self._view.create_alert("I prodotti di partenza e arrivo devono essere diversi")
            return
        path, peso = self._model.getCammino(start, end, lun)
        self._view.txt_result.controls.clear()
        if path is None:
            self._view.txt_result.controls.append(
                ft.Text(f"Nessun cammino di lunghezza {lun} trovato tra {start} e {end}"))
        else:
            self._view.txt_result.controls.append(ft.Text(f"Cammino trovato con peso totale {peso}:"))
            for node in path:
                self._view.txt_result.controls.append(ft.Text(f"{node}"))
        self._view.update_page()

    def setDates(self):
        first, last = self._model.getDateRange()
        if first is None or last is None:
            self._view.create_alert("Errore nel caricamento delle date dal database")
            return
        self._view._dp1.first_date = datetime.date(first.year, first.month, first.day)
        self._view._dp1.last_date = datetime.date(last.year, last.month, last.day)
        self._view._dp1.current_date = datetime.date(first.year, first.month, first.day)
        self._view._dp2.first_date = datetime.date(first.year, first.month, first.day)
        self._view._dp2.last_date = datetime.date(last.year, last.month, last.day)
        self._view._dp2.current_date = datetime.date(last.year, last.month, last.day)
