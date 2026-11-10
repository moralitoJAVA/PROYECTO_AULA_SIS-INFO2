from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from src.constantes import FORMATO_FECHA_HORA_PDF


class GeneradorPdfRespuesta:
    """Arma el PDF de la respuesta del estudiante con la fecha y hora exactas del envío."""

    def generar(self, respuesta, clase):
        estilos = getSampleStyleSheet()
        buffer = BytesIO()
        documento = SimpleDocTemplate(buffer, pagesize=A4, title=respuesta.titulo, pageCompression=0)
        cuerpo = escape(respuesta.respuesta).replace("\n", "<br/>")
        partes = [
            Paragraph(escape(respuesta.titulo), estilos["Title"]),
            Paragraph(f"Estudiante: {escape(respuesta.estudiante)}", estilos["Normal"]),
            Paragraph(f"Clase: {escape(clase.tema)}", estilos["Normal"]),
            Paragraph("Enviado: " + FORMATO_FECHA_HORA_PDF.format(fecha=respuesta.fecha_hora_envio), estilos["Normal"]),
            Paragraph(f"Estado: {respuesta.puntualidad.value}", estilos["Normal"]),
            Spacer(1, 18),
            Paragraph(cuerpo, estilos["BodyText"]),
        ]
        documento.build(partes)
        return buffer.getvalue()