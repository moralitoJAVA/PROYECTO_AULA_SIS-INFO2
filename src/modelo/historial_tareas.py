from decimal import ROUND_HALF_UP, Decimal

from src.constantes import CENTESIMOS, CERO, CIEN, ESTADOS_TAREA


class HistorialTareas:
    def __init__(self, tareas, entregas):
        self._tareas = list(tareas)
        self._entregas = dict(entregas)

    def ordenarPorFecha(self, items):
        return sorted(items, key=lambda item: item["fecha_limite"])

    def _notaFinal(self, entrega):
        if entrega is None or entrega.nota is None:
            return None
        con_descuento = entrega.nota * (CIEN - entrega.descuento) / CIEN
        return con_descuento.quantize(CENTESIMOS, rounding=ROUND_HALF_UP)

    def listarPorEstado(self, estado=None):
        items = []
        for tarea in self._tareas:
            entrega = self._entregas.get(tarea.numero)
            estado_actual = entrega.estado if entrega else ESTADOS_TAREA.PENDIENTE
            if estado is None or estado_actual == estado:
                items.append({
                    "numero": tarea.numero,
                    "titulo": tarea.titulo,
                    "fecha_limite": tarea.fecha_limite,
                    "tipo": tarea.tipo.value,
                    "estado": estado_actual,
                    "nota": entrega.nota if entrega else None,
                    "descuento": entrega.descuento if entrega else CERO,
                    "nota_final": self._notaFinal(entrega),
                })
        return self.ordenarPorFecha(items)

    def obtenerNotas(self):
        notas = []
        for numero, entrega in sorted(self._entregas.items()):
            if entrega.estado == ESTADOS_TAREA.CALIFICADA:
                sobre_cien = entrega.nota * CIEN / entrega.puntaje_maximo
                notas.append({
                    "numero": numero,
                    "nota_sobre_100": sobre_cien.quantize(CENTESIMOS, rounding=ROUND_HALF_UP),
                    "descuento": entrega.descuento,
                })
        return notas