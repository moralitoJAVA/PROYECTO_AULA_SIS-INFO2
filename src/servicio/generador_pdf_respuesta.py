from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

FORMATO_FECHA_HORA = "%d/%m/%Y %H:%M:%S"


class GeneradorPdfRespuesta:
    """Genera el PDF de una respuesta de clase. Sin compresion para que el texto quede legible en el documento."""

    def generar(self, respuesta, clase):
        buffer = BytesIO()
        lienzo = canvas.Canvas(buffer, pagesize=A4, pageCompression=0)
        ancho, alto = A4
        margen = 2 * cm
        y = alto - margen

        lienzo.setFont("Helvetica-Bold", 16)
        lienzo.drawString(margen, y, "Respuesta de clase")
        y -= 1.2 * cm

        fecha_hora = respuesta.fecha_hora_envio.strftime(FORMATO_FECHA_HORA)
        puntualidad = respuesta.puntualidad.value
        encabezado = [
            ("Estudiante", respuesta.estudiante),
            ("Titulo", respuesta.titulo),
            ("Fecha y hora de envio", fecha_hora),
            ("Puntualidad", puntualidad),
        ]
        lienzo.setFont("Helvetica", 11)
        for etiqueta, valor in encabezado:
            lienzo.drawString(margen, y, f"{etiqueta}: {valor}")
            y -= 0.8 * cm

        y -= 0.4 * cm
        lienzo.setFont("Helvetica-Bold", 12)
        lienzo.drawString(margen, y, "Respuesta")
        y -= 0.8 * cm

        lienzo.setFont("Helvetica", 11)
        ancho_util = ancho - 2 * margen
        for linea in self._ajustar(respuesta.respuesta, ancho_util, lienzo):
            if y < margen:
                lienzo.showPage()
                lienzo.setFont("Helvetica", 11)
                y = alto - margen
            lienzo.drawString(margen, y, linea)
            y -= 0.6 * cm

        lienzo.showPage()
        lienzo.save()
        return buffer.getvalue()

    @staticmethod
    def _ajustar(texto, ancho_disponible, lienzo):
        lineas = []
        for parrafo in (texto or "").splitlines() or [""]:
            actual = ""
            for palabra in parrafo.split():
                tentativa = f"{actual} {palabra}".strip()
                if lienzo.stringWidth(tentativa, "Helvetica", 11) <= ancho_disponible:
                    actual = tentativa
                else:
                    if actual:
                        lineas.append(actual)
                    actual = palabra
            lineas.append(actual)
        return lineas
