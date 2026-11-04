from src.constantes import ESTADOS, MSG_ESTADO_INVALIDO, MSG_NO_REGISTRADA, MSG_YA_REGISTRADA


class Asistencia:
    def __init__(self):
        self._registros = {}

    @property
    def registros(self):
        return dict(self._registros)

    def validarEstado(self, estado):
        if not isinstance(estado, ESTADOS):
            raise ValueError(MSG_ESTADO_INVALIDO)

    def existePara(self, fecha):
        return fecha in self._registros

    def registrar(self, fecha, estado):
        self.validarEstado(estado)
        if self.existePara(fecha):
            raise ValueError(MSG_YA_REGISTRADA)
        self._registros[fecha] = estado

    def editar(self, fecha, estado):
        self.validarEstado(estado)
        if not self.existePara(fecha):
            raise ValueError(MSG_NO_REGISTRADA)
        self._registros[fecha] = estado
