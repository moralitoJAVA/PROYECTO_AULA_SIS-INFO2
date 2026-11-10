import base64
import smtplib
from email.message import EmailMessage


class EnviadorCorreo:
    """Envía el correo real al docente vía SMTP. Se inyecta para poder probar el servicio sin un servidor de correo."""

    def __init__(self, host="localhost", puerto=25, remitente="aula@umss.edu.bo", usuario=None, clave=None):
        self._host = host
        self._puerto = puerto
        self._remitente = remitente
        self._usuario = usuario
        self._clave = clave

    def enviar(self, destino, asunto, cuerpo, adjuntos):
        mensaje = EmailMessage()
        mensaje["From"] = self._remitente
        mensaje["To"] = destino
        mensaje["Subject"] = asunto
        mensaje.set_content(cuerpo)
        for adjunto in adjuntos:
            contenido = adjunto.get("contenido")
            datos = base64.b64decode(contenido) if contenido else b""
            mensaje.add_attachment(datos, maintype="application", subtype="octet-stream",
                                   filename=adjunto.get("nombre", "adjunto"))
        with smtplib.SMTP(self._host, self._puerto) as servidor:
            if self._usuario:
                servidor.starttls()
                servidor.login(self._usuario, self._clave)
            servidor.send_message(mensaje)
