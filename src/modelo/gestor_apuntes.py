from src.constantes import MSG_APUNTE_NO_EXISTE, MSG_APUNTE_VACIO


class GestorApuntes:
    def __init__(self, repositorio):
        self._repositorio = repositorio

    def _validar(self, texto):
        if texto is None or not str(texto).strip():
            raise ValueError(MSG_APUNTE_VACIO)
        return str(texto).strip()

    def crear(self, vinculo, texto):
        texto = self._validar(texto)
        clave = str(max([int(k) for k in self._repositorio.listar()] + [0]) + 1)
        self._repositorio.guardar(clave, {"vinculo": vinculo, "texto": texto})
        return clave

    def editar(self, clave, texto):
        apunte = self._repositorio.obtener(clave)
        if apunte is None:
            raise ValueError(MSG_APUNTE_NO_EXISTE)
        apunte["texto"] = self._validar(texto)
        self._repositorio.guardar(clave, apunte)

    def borrar(self, clave):
        if self._repositorio.obtener(clave) is None:
            raise ValueError(MSG_APUNTE_NO_EXISTE)
        self._repositorio.eliminar(clave)

    def listarApuntes(self, vinculo=None):
        return [
            {"clave": clave, **apunte}
            for clave, apunte in sorted(self._repositorio.listar().items(), key=lambda par: int(par[0]))
            if vinculo is None or apunte["vinculo"] == vinculo
        ]